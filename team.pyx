import random
import numpy as np
import math
from player import Player
from prospect import Prospect, fv_walk, eta_matrix
from aging_regression import adjust_prospect_war, predict_start_ratio_fast, predict_start_ratio, average, war_predictor_fast
from scipy import integrate

cdef int PRE_ARB = 563_500  # salary for players in pre-arbitration
cdef float VESTING_THRESHOLD = 0.5  # WAR threshold for vesting contract years

cdef int DOLLAR_PER_WAR = 9_100_000  # market value for WAR
# ^^^ loosely based on this research: https://blogs.fangraphs.com/the-cost-of-a-win-in-free-agency-in-2020/

cdef float SQRT2PI = math.sqrt(2 * math.pi)

DRAFT_PICKS = 5
J2_SIGNINGS = 3

# Based on Fangraphs FV to average WAR values

PITCHER_FV_DICT = {
    20: 0.0,
    25: 0.0,
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
    20: 0.0,
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

# Prospect Nerf
"""
nerf = 0.00
PITCHER_FV_DICT = {k: v * (1 - nerf) for k, v in PITCHER_FV_DICT.items()} 
BATTER_FV_DICT = {k: v * (1 - nerf) for k, v in BATTER_FV_DICT.items()} 
"""


# function based on model from arbitration.r
cdef get_arb_salary(war, age, arb_years_remaining=1):
    cdef float new_salary = 16639108  - age * 357730 + war * 1180929

    if arb_years_remaining == 0:
        new_salary -= 2729314
    elif arb_years_remaining == 1:
        new_salary -= 3840663
    elif arb_years_remaining >= 2:
        new_salary -= 5810577

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
    
    # A version of age players that does not rely on the player.develop() function
    # Speeds up the process by getting WAR for all players on a team at the same time
    def age_players_fast(self):
        
        # Add one to all ages before getting WAR
        for cont in self.contracts:
            cont['player'].age += 1

        pitcher_args = [[x['player'].age, x['player'].wars[-1], average(x['player'].wars), x['player'].start_ratio] for x in self.contracts if x['player'].pitcher]
        batter_args = [[x['player'].age, x['player'].wars[-1], average(x['player'].wars)] for x in self.contracts if not x['player'].pitcher]

        all_wars = war_predictor_fast(pitcher_args, batter_args)
        pitcher_i = 0
        batter_i = 0
        for i in range(len(self.contracts)):
            if self.contracts[i]['player'].pitcher:
                self.contracts[i]['player'].wars.append(all_wars[0][pitcher_i])
                pitcher_i += 1
            else:
                self.contracts[i]['player'].wars.append(all_wars[1][batter_i])
                batter_i += 1

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
                new_war = [adjust_prospect_war(new_war, prospect.age, prospect.pitcher)]
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

    def age_prospects_fast(self):
        num_prospects = len(self.prospects)
        # FV Draw
        fv_draws = np.random.choice(np.arange(-2, 3), num_prospects, p=fv_walk)
        
        # ETA Draw
        eta_draws = np.random.random_sample(num_prospects)

        for i in range(num_prospects):
            pros = self.prospects[i]
            if pros.dead:
                continue
            
            pros.age += 1

            pros.fv = min(max(pros.fv + 5 * fv_draws[i], 20), 80)
            eta_draw = eta_draws[i]
            
            eta_sums = list()
            prev_sum = 0  # memoization
            for i in range(8):
                prev_sum += eta_matrix[pros.eta][i]
                eta_sums.append(prev_sum)

            if eta_draw < eta_sums[0]:
                pros.eta = 0
            elif eta_draw < eta_sums[1]:
                pros.eta = 1
            elif eta_draw < eta_sums[2]:
                pros.eta = 2
            elif eta_draw < eta_sums[3]:
                pros.eta = 3
            elif eta_draw < eta_sums[4]:
                pros.eta = 4
            elif eta_draw < eta_sums[5]:
                pros.eta = 5
            elif eta_draw < eta_sums[6]:
                pros.eta = 6
            else:
                pros.dead = True
        
        eta_0s = list(filter(lambda x: x.eta == 0, self.prospects))
        num_new_mlbers = len(eta_0s)
        if num_new_mlbers > 0:
            new_wars = [[PITCHER_FV_DICT[pros.fv]] if pros.pitcher else [BATTER_FV_DICT[pros.fv]] for pros in eta_0s]
            startses = predict_start_ratio_fast(new_wars)

            for i in range(num_new_mlbers):
                pros = eta_0s[i]
                new_id = pros.name
                new_war = new_wars[i][0]
                starts = min(startses[i], 1)
                new_war = [adjust_prospect_war(new_war, pros.age, pros.pitcher)]
                new_player = Player(new_id, new_war, pros.age, pros.pitcher, starts, name=pros.name,
                                    sim_grown=True)

                # Three years of pre-arb, three years of arb
                new_payouts = [{'type': 'pre-arb', 'value': PRE_ARB}, {'type': 'pre-arb', 'value': PRE_ARB},
                                {'type': 'pre-arb', 'value': PRE_ARB}, {'type': 'arb', 'value': None},
                                {'type': 'arb', 'value': None}, {'type': 'arb', 'value': None}]

                self.contracts.append({'player': new_player, 'payouts': new_payouts})
        
        self.prospects = list(filter(lambda x: x.eta != 0 and not x.dead, self.prospects))


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

        mu = (team_war + (162 * .294)) / 162
        sigma = 0.0309  # mean and standard deviation of WL%

        # Argument is wl
        def integrand_wl(x):
            return 1 / (sigma * SQRT2PI) * math.exp(-.5 * math.pow((x - mu) / sigma, 2))

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
        # .35 to .80 for performance reasons (rather than 0 to 1)
        div_round = integrate.quad(lambda x: integrand_div_round(x) * integrand_wl(x), 0.35, .80)[0]

        return ws * div_round

    def record_year(self):
        cdef float tots = self.get_team_war()
        to_add = {
            'Total WAR': tots,
            'FA WAR': self.last_fa_war,
            'Sim Prospect WAR': sum([(x['player'].wars[-1]) for x in self.contracts if x['player'].sim_grown]),
            'Max Payroll': self.max_payroll,
            'Championship Probability': self.get_championship_prob(tots)
        }
        self.records.append(to_add)

    def get_contract_values(self):
        cdef float tots = 0
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
            # Super 2 should be implemented

            # Set salary for pre-arb and arb
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
            elif remaining_payouts[0]['type'] == 'player option':
                # Opposite of team option
                if remaining_payouts[0]['value'] / player['player'].get_war() < DOLLAR_PER_WAR:
                    continue
            elif remaining_payouts[0]['type'] == 'mutual option':
                continue

            player['payouts'] = remaining_payouts

            new_contracts.append(player)

        self.contracts = new_contracts

    # Add july 2nd signings
    def add_ifas(self, num_signings):
        
        ages = np.random.choice(np.arange(17, 24), num_signings, p=[.94, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01])
        etas_young = np.random.choice(np.arange(1, 7), num_signings, p=[.005, .01, .05, .25, .335, .35])
        etas_old = np.random.choice(np.arange(1, 7), num_signings, p=[.01, .05, .35, .25, .24, .10])
        positions = np.random.random_sample(num_signings)
        fvs = np.random.choice(np.arange(7, 14), num_signings, p=[.31, .50, 0.10, 0.06, .015, .01, .005])

        for i in range(num_signings):
            age = ages[i]
            eta = etas_young[i] if age < 20 else etas_old[i]
            position = positions[i] < .5
            # Based on The Board distribution
            fv = 5 * fvs[i]
            prospect = Prospect(eta, fv, age, position, name=str(random.randint(0, 100000)) + " J2")
            self.prospects.append(prospect)

    def add_draft_picks(self, num_picks, starting_round=1):
        # Values inferred from: https://blogs.fangraphs.com/an-update-to-prospect-valuation/
        # and https://academicworks.cuny.edu/cgi/viewcontent.cgi?article=1759&context=cc_etds_theses

        cdef float most_recent_war
        if len(self.records) == 0:
            # Probably because you're adding fake draft prospects before sim
            most_recent_war = 35  # average team
        else:
            most_recent_war = self.records[-1]['Total WAR']

        # Note: this line should be replaced with the real win loss if that's calculated in the sim
        cdef float wl = ((.294 * 162 + most_recent_war) / 162)  # Replacement level team is .294

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

        ages = np.random.choice(np.arange(17, 24), num_picks, p=[.05, .28, .04, .06, .55, .01, .01])
        etas_young = np.random.choice(np.arange(1, 7), num_picks, p=[.005, .01, .05, .25, .335, .35])
        etas_old = np.random.choice(np.arange(1, 7), num_picks, p=[.01, .05, .35, .25, .24, .10])
        positions = np.random.random_sample(num_picks)

        cdef int pick_num
        cdef int age
        cdef int eta
        for r in range(starting_round - 1, num_picks + starting_round - 1):
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

            i = r - starting_round + 1

            position = positions[i] > .5
            # Loosely based off of 2020 figures so far
            age = ages[i]
            # Different ETA rules for college vs. high school
            eta = etas_young[i] if age < 20 else etas_old[i]
            prospect = Prospect(eta, fv, age, position, name=f"{int(random.random() * 100000)} D{r}")
            self.prospects.append(prospect)

    def run_year(self):
        self.age_players_fast()  # Ages players by a year, gets new WAR value
        self.age_prospects_fast()  # Ages prospects, develops by a year, adds to MLB if needed
        self.add_player_variance()  # Adds in-season noise

        if self.max_payroll is None:
            self.max_payroll = self.get_contract_values()

        self.record_year()  # Collects WAR for players, prospects, and FA
        self.update_contracts()  # Progresses contracts by a year

        # Assumes each team picks 5 players - only looking for top prospects here (simulating Fangraphs' The Board)
        self.add_draft_picks(DRAFT_PICKS)
        # Based on analysis, draft prospects outnumber J2 signings close to 1.7-1
        self.add_ifas(J2_SIGNINGS)

    def run_years(self, num_years):
        for _ in range(num_years):
            self.run_year()
