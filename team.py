import random
import numpy as np
from player import Player

PRE_ARB = 563_500  # salary for players in pre-arbitration, currently just the MLB minimum
VESTING_THRESHOLD = 0.5  # WAR threshold for vesting contract years

DOLLAR_PER_WAR = 8_000_000  # market value for WAR - $8m/win
# ^^^ based on this research: https://blogs.fangraphs.com/the-cost-of-a-win-in-free-agency-in-2020/

# Based on Fangraphs FV to average WAR values

pitcher_fv_dict = {
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

batter_fv_dict = {
    20: -0.1,
    25: 0,
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
        a) wins (int)
        b) losses (int)
        c) div_place (int)
        d) outcome (string - empty or WC or DS or CS or WS)
    7. max_payroll (float) | Total team payroll

    """

    def __init__(self, name, division, league, contracts, prospects, max_payroll=None):
        self.name = name
        self.division = division
        self.league = league

        self.contracts = contracts
        self.prospects = prospects

        self.records = []

        # if max_payroll isn't set, it becomes whatever the initial payroll is
        if max_payroll is None:
            self.max_payroll = self.get_contract_values()
        else:
            self.max_payroll = max_payroll

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

    def age_prospects(self):
        # Replaces prospect list with new list, excluding new MLB players and dead prospects
        new_prospects = []
        for prospect in self.prospects:
            prospect.develop()
            if prospect.eta == 0:
                # ID is made up of a random number and the name
                new_id = prospect.name.lower().replace(" ", "") + str(random.randint(0, 1_000_000))
                new_war = pitcher_fv_dict[prospect.fv] if prospect.pitcher else batter_fv_dict[prospect.fv]
                new_player = Player(new_id, [new_war], prospect.age, prospect.pitcher, name=prospect.name)

                # Three years of pre-arb, three years of arb
                new_payouts = [{'type': 'pre-arb', 'value': PRE_ARB}, {'type': 'pre-arb', 'value': PRE_ARB}, {'type': 'pre-arb', 'value': PRE_ARB}, {'type': 'arb', 'value': None}, {'type': 'arb', 'value': None}, {'type': 'arb', 'value': None}]

                self.contracts.append({'player': new_player, 'payouts': new_payouts})
            elif not prospect.dead:
                new_prospects.append(prospect)
        self.prospects = new_prospects

    def get_fa_war(self):
        # note: fa_allocation could be negative!
        fa_allocation = self.max_payroll - self.get_contract_values()
        fa_mu = fa_allocation / DOLLAR_PER_WAR
        fa_std_dev = fa_mu / 4  # 4 is arbitrary - goal is to scale with the mu WAR
        return np.random.normal(fa_mu, fa_std_dev, 1)[0]

    def get_team_war(self):
        wars = []
        for player in self.contracts:
            wars.append(player['player'].get_war())
        wars.sort(reverse=True)
        return sum(wars[:40])

    def record_year(self):
        self.records.append({'Total WAR': self.get_team_war()})

    def get_contract_values(self):
        return sum([x['payouts']['value'] for x in self.contracts])
    
    # Adds new prospects from draft and J2 – only top prospects
    def add_new_prospects(self):
        # Values inferred from: https://blogs.fangraphs.com/an-update-to-prospect-valuation/
        # and https://academicworks.cuny.edu/cgi/viewcontent.cgi?article=1759&context=cc_etds_theses

        # Go through draft:
        most_recent_war = self.records[-1]['Total WAR']
        # TODO
        pick = ((.294 * 162 + most_recent_war) / 162) * 30  # Replacement level team is .294
        pick = round(pick)

        for r in range(40):
            # TODO: get empirical percentage of prospects that are pitchers
            position = np.random.choice([True, False], 1, True, [.2, .8])[0]

            pick_num = pick * r
            if pick == 1:
                pass

    def update_contracts(self):
        new_contracts = []
        for player in self.contracts:
            if len(player['payouts']) <= 1:
                continue
            remaining_payouts = player['payouts'][1:]

            # TODO Problems:
            # Pre-arb figures should be checked
            # Arb model should be compared with empirical data
            # Vesting option model should be compared with empirical data
            # Player and team options automatically execute, so this needs to be worked out
            # Super 2 should be implemented

            # Set salary for pre-arb and arb
            # Pre-arb technically uncessary, but just as a check
            if remaining_payouts[0]['type'] == 'pre-arb':
                remaining_payouts[0]['value'] = PRE_ARB
            elif remaining_payouts[0]['type'] == 'arb':
                # Linear conversion from WAR to arb $, depending on how many years of arb left
                # Values at the moment are arbitrary but should be replaced with empirically correct values
                arb_years_remaining = sum(x['type'] == 'arb' for x in remaining_payouts)
                if arb_years_remaining == 0:
                    dol_per_war = 4_000_000
                elif arb_years_remaining == 1:
                    dol_per_war = 3_000_000
                elif arb_years_remaining >= 2:
                    dol_per_war = 2_000_000
                remaining_payouts[0]['value'] = min(player['player'].get_war() * dol_per_war, PRE_ARB)
            elif remaining_payouts[0]['type'] == 'vesting option':
                if player['player'].get_war() < VESTING_THRESHOLD:
                    continue
            # Player and team options automatically execute

            player['payouts'] = remaining_payouts

            new_contracts.append(player)


    def run_year(self):
        self.age_players()  # Ages players by a year, gets new WAR value 
        self.age_prospects()  # Ages prospects, develops by a year, adds to MLB if needed
        self.record_year()  # Collects WAR for players, prospects, and FA
        self.update_contracts()  # Progresses contracts by a year
        self.add_new_prospects()  # Conducts draft and J2 signings
