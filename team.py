import random
import string
import numpy as np
import math
from player import Player
from prospect import Prospect
from aging_regression import adjust_prospect_war, predict_start_ratio
from scipy import integrate

PRE_ARB = 563_500  # salary for players in pre-arbitration, currently just the MLB minimum
VESTING_THRESHOLD = 0.5  # WAR threshold for vesting contract years

DOLLAR_PER_WAR = 7_500_000  # market value for WAR
# ^^^ loosely based on this research: https://blogs.fangraphs.com/the-cost-of-a-win-in-free-agency-in-2020/

# Based on Fangraphs FV to average WAR values

PITCHER_FV_DICT = {
    20: -0.1,
    25: 0,
    30: 0.0,
    35: 0.1,
    40: 0.45,
    45: 1.35,
    50: 2.15,
    55: 3,
    60: 4.2,
    65: 5.1,
    70: 6,
    75: 6.5,
    80: 7
}

BATTER_FV_DICT = {
    20: -0.1,
    25: 0.0,
    30: 0.0,
    35: 0.1,
    40: 0.35,
    45: 1.15,
    50: 2,
    55: 2.9,
    60: 4.15,
    65: 5,
    70: 6,
    75: 6.5,
    80: 7
}


# function based on model from arbitration.r
def get_arb_salary(war, age, arb_years_remaining=1):
    new_salary = 16_639_108  # intercept
    new_salary = new_salary - age * 357_730
    new_salary = new_salary + war * 1_180_929

    if arb_years_remaining == 0:
        new_salary -= 2_729_314
    elif arb_years_remaining == 1:
        new_salary -= 3_840_663
    elif arb_years_remaining >= 2:
        new_salary -= 5_810_577

    return new_salary
    

class Team:
    """
    A team has, for variables:
    1. name (string) | Name of MLB team
    2. division (int) | MLB division - 6 total
    3. league (string - NL or AL) | MLB league
    4. contracts (list of dictionaries with -) | All the existing contracts of the team
        a) player (Player object) | Player of the contract
        b) payouts (list of dictionaries) | Type of year (option, normal salary, etc.) and value for year in $
    5. prospects (list of Prospect objects) | Farm system
    6. records (list of dictionaries with -) | Season outcomes
        a) Team WAR (float)
        b) FA WAR (float)
        c) Sim Prospect WAR (float)
        d) Max Payroll (float)
        e) Championship Probability (float)
    7. max_payroll (float) | Total team payroll
    """

    def __init__(self, name, division, league, contracts, prospects, max_payroll=None):
        self.name = name
        self.division = division
        self.league = league

        self.contracts = contracts
        self.prospects = prospects
        self.backups = []

        self.records = []

        # if max_payroll isn't set, it becomes whatever the initial payroll is in the first year - set in run_year()
        self.max_payroll = max_payroll

        self.last_fa_war = 0  # For record keeping

    def add_prospect(self, new_prospect):
        self.prospects.append(new_prospect)

    # Takes list of prospects as argument
    def add_prospects(self, new_prospects):
        self.prospects.extend(new_prospects)

    def add_contract(self, player, payouts):
        """
        player: player object
        payouts: list of dictionaries
        dictionaries:
        {
           'type':'team option', 'salary', 'vesting option', 'player option',
                    'pre-arb', 'arb'
           'value': $
        }
        """
        self.contracts.append({'player': player, 'payouts': payouts})

    def age_players(self):
        for player in self.contracts:
            player['player'].progress()

    def add_player_variance(self):
        for player in self.contracts:
            player['player'].add_variance()

    def age_prospects(self):
        # Replaces prospect list with new list, excluding new MLB players and dead prospects
        new_prospects = []
        for prospect in self.prospects:
            prospect.develop()
            if prospect.eta == 0:
                new_id = prospect.name
                new_war = PITCHER_FV_DICT[prospect.fv] if prospect.pitcher else BATTER_FV_DICT[prospect.fv]
                starts = predict_start_ratio(new_war)
                new_war = [adjust_prospect_war(new_war, prospect.age, prospect.pitcher) - .25]
                new_player = Player(new_id, new_war, prospect.age, prospect.pitcher, starts, name=prospect.name,
                                    sim_grown=True)

                # Three years of pre-arb, three years of arb
                new_payouts = [{'type': 'pre-arb', 'value': PRE_ARB}, {'type': 'pre-arb', 'value': PRE_ARB},
                               {'type': 'pre-arb', 'value': PRE_ARB}, {'type': 'arb', 'value': None},
                               {'type': 'arb', 'value': None}, {'type': 'arb', 'value': None}]

                self.contracts.append({'player': new_player, 'payouts': new_payouts})
            elif not prospect.dead:
                new_prospects.append(prospect)
        self.prospects = new_prospects

    def get_fa_war(self):
        # note: fa_allocation could be negative!
        fa_allocation = self.max_payroll - self.get_contract_values()
        fa_mu = fa_allocation / DOLLAR_PER_WAR
        fa_std_dev = fa_mu / 1.5  # the constant is arbitrary - goal is to scale with the mu WAR
        # Note: FA standard deviation is a major tool to affect late-sim WS probability while keeping WL% constant
        return np.random.normal(fa_mu, abs(fa_std_dev), 1)[0]

    def get_team_war(self):

        war = 0
        for player in self.contracts:
            war += player['player'].get_war()
        self.last_fa_war = self.get_fa_war()
        war += self.last_fa_war
        return war
    
    # Uses analytical method – not comparison to other teams in the sim
    def get_championship_prob(self, team_war):
        mu, sigma = (team_war + (162 * .294)) / 162, 0.0309  # mean and standard deviation of WL%

        # Argument is wl
        def integrand_wl(x):
            y = 1 / (sigma * math.sqrt(2 * math.pi)) * math.exp(-.5 * ((x - mu) / sigma) ** 2)
            return y

        # Argument is wl
        def integrand_div(x):
            return 1 / (1 + math.exp(-(-31 + 53 * x)))

        # Argument is wl
        def integrand_ploffs(x):
            return 1 / (1 + math.exp(-(-54.7 + 100 * x)))

        def integrand_div_round(x):
            d = integrand_div(x)
            return d + .5 * (integrand_ploffs(x) - d)

        # Argument is WAR
        def integrand_ws(x):
            return 1 / (1 + math.exp(-(-4.14 + 0.0472 * x)))

        ws = integrand_ws(team_war)
        div_round = integrate.quad(lambda x: integrand_div_round(x) * integrand_wl(x), 0, 1)[0]

        return ws * div_round

    def record_year(self):
        tots = self.get_team_war()
        to_add = {
            'Total WAR': tots,
            'FA WAR': self.last_fa_war,
            'Sim Prospect WAR': sum([(x['player'].wars[-1] if x['player'].sim_grown else 0) for x in self.contracts]),
            'Max Payroll': self.max_payroll,
            'Championship Probability': self.get_championship_prob(tots)
        }
        self.records.append(to_add)

    def get_contract_values(self):
        # return sum([x['payouts'][0]['value'] for x in self.contracts])
        tots = 0
        for cont in self.contracts:
            try:
                if cont['payouts'][0]['type'] == "arb" and cont['payouts'][0]['value'] is None:
                    tots += get_arb_salary(cont['player'].get_war(), cont['player'].age)
                else:
                    tots += cont['payouts'][0]['value']
            except:  # Sloppy!
                pass
        return tots

    def update_contracts(self):
        new_contracts = []
        for player in self.contracts:
            if len(player['payouts']) <= 1:
                continue
            remaining_payouts = player['payouts'][1:]

            # TODO Problems:
            # Vesting option model should be compared with empirical data
            # Player options automatically execute, so this needs to be worked out
            # Super 2 should be implemented

            # Set salary for pre-arb and arb
            # Pre-arb technically uncessary, but just as a check
            if remaining_payouts[0]['type'] == 'pre-arb':
                remaining_payouts[0]['value'] = PRE_ARB
            elif remaining_payouts[0]['type'] == 'arb':
                arb_years_remaining = sum(x['type'] == 'arb' for x in remaining_payouts)
                remaining_payouts[0]['value'] = max(get_arb_salary(player['player'].get_war(), player['player'].age,
                                                                   arb_years_remaining=arb_years_remaining), PRE_ARB)
            elif remaining_payouts[0]['type'] == 'vesting option':
                if player['player'].get_war() < VESTING_THRESHOLD:
                    continue
            elif remaining_payouts[0]['type'] == 'team option':
                # Uses previous year WAR, not prediction
                if remaining_payouts[0]['value'] / player['player'].get_war() > DOLLAR_PER_WAR:
                    continue
            elif remaining_payouts[0]['type'] == 'mutual option':
                continue

            player['payouts'] = remaining_payouts

            new_contracts.append(player)

        self.contracts = new_contracts

    # Add july 2nd signings
    def add_ifas(self, num_signings):
        for _ in range(num_signings):
            age = np.random.choice(np.arange(17, 24), 1, p=[.94, .01, .01, .01, .01, .01, .01])[0]
            if age < 20:
                eta = np.random.choice(np.arange(1, 7), 1, p=[.0, .005, .005, .05, 0.09, 0.85])[0]
            else:
                eta = np.random.choice(np.arange(1, 7), 1, p=[.015, .025, 0.08, 0.18, .39, .31])[0]
            position = random.random() > .5
            # Based on The Board distribution
            fv = 5 * np.random.choice(np.arange(7, 14), 1, p=[.31, .50, 0.10, 0.06, .015, .01, .005])[0]
            prospect = Prospect(eta, fv, age, position, name=str(random.randint(0, 100000)) + " J2")
            self.prospects.append(prospect)

    def add_draft_picks(self, num_picks, starting_round=1):
        # Values inferred from: https://blogs.fangraphs.com/an-update-to-prospect-valuation/
        # and https://academicworks.cuny.edu/cgi/viewcontent.cgi?article=1759&context=cc_etds_theses

        try:
            most_recent_war = self.records[-1]['Total WAR']
        except IndexError:
            # Probably because you're adding fake draft prospects before sim
            most_recent_war = 35  # average team

        # Note: this line should be replaced with the real win loss if that's calculated in the sim
        wl = ((.294 * 162 + most_recent_war) / 162)  # Replacement level team is .294

        # Based on empirical analysis
        if wl < .395:
            pick = 1  # Is actually the first or second
        elif wl < .451:
            pick = 3  # is actually 3-8
        elif wl < .512:
            pick = 9  # is actually 9-16
        elif wl < .593:
            pick = 17  # is actually 17-27
        else:
            pick = 28  # is actually 28-30

        for r in range(starting_round - 1, num_picks):
            position = random.random() > .5

            pick_num = pick * r
            if pick_num <= 2:
                fv = 60
            elif pick_num <= 8:
                fv = 55
            elif pick_num <= 16:
                fv = 50
            elif pick_num <= 57:
                fv = 45
            else:
                fv = 40

            # Loosely based off of 2020 figures so far
            age = np.random.choice(np.arange(17, 24), 1, p=[6/124, 34/124, 4/124, 8/124, 69/124, 2/124, 1/124])[0]
            # Different ETA rules for college vs. high school
            if age < 20:
                eta = np.random.choice(np.arange(1, 7), 1, p=[.0, .005, .005, .05, 0.09, 0.85])[0]
            else:
                eta = np.random.choice(np.arange(1, 7), 1, p=[.015, .025, 0.08, 0.18, .39, .31])[0]

            prospect = Prospect(eta, fv, age, position, name=str(random.randint(0, 100000)) + " D" + str(r))
            self.prospects.append(prospect)

    # Adds new prospects from draft and J2 – only top prospects
    def add_new_prospects(self):
        # Assumes each team picks 6 players - only looking for top prospects here (simulating Fangraphs' The Board)
        self.add_draft_picks(6)
        # Based on analysis, draft prospects outnumber J2 signings close to 1.7-1
        self.add_ifas(random.randint(3, 4))

    def run_year(self):
        self.age_players()  # Ages players by a year, gets new WAR value
        self.age_prospects()  # Ages prospects, develops by a year, adds to MLB if needed
        self.add_player_variance()  # Adds in-season noise

        if self.max_payroll is None:
            self.max_payroll = self.get_contract_values()

        self.record_year()  # Collects WAR for players, prospects, and FA
        self.update_contracts()  # Progresses contracts by a year

        self.add_new_prospects()  # Conducts draft and J2 signings

    def run_years(self, num_years):
        for _ in range(num_years):
            self.run_year()
