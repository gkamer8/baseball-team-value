import csv
import random
from aging import batting_models, pitching_models, age_bucket_mapper, war_bucket_mapper
from player_class import Player
import numpy as np

aging_batters, aging_pitchers = batting_models, pitching_models

PRE_ARB = 563_500  # salary for players in pre-arbitration, currently just the MLB minimum
VESTING_THRESHOLD = 0.5  # WAR threshold for vesting contract years

DOLLAR_PER_WAR = 8_000_000  # market value for WAR - $8m/win
# ^^^ based on this research: https://blogs.fangraphs.com/the-cost-of-a-win-in-free-agency-in-2020/

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
        self.age_players()
        self.age_prospects()
        self.record_year()
        self.update_contracts()


# Inherits Player?
class Prospect:

    """

    A prospect has, for variables:
    1. eta - (int) | Estimated time of arrival - # of years
    2. fv - (int) | Future value from Fangraphs
    3. dead - (bool) | Is the player irrecovably injured/otherwise hopeless
    4. age - (int) | Age of player
    5. pitcher - (bool) | Whether or not the prospect is a pitcher
    6. name - (string) | Optional name of prospect

    """

    def __init__(self, eta, fv, age, pitcher, name=""):
        self.eta = eta
        self.fv = fv
        self.dead = False
        self.age = age
        self.pitcher = pitcher

        self.name = name

    # Develop one year
    # Process is loosely based on historical data from Fangraphs scouting results
    def develop(self):
        self.age += 1  # Prospect ages 1 year

        # Evolve FV
        # Random walk with probabilities below
        # -2    -1    0    1    2
        # .125 .25  .35  .25 .125
        fv_draw = random.random()
        if fv_draw < .125:
            self.fv = max(self.fv - 10, 20)
        elif fv_draw < .125 + .25:
            self.fv = max(self.fv - 5, 20)
        elif fv_draw < .125 + .25 + .35:
            pass
        elif fv_draw < .125 + .25 + .35 + .25:
            self.fv = min(self.fv + 5, 80)
        else:
            self.fv = min(self.fv + 10, 80)

        # Evolve ETA
        # Markov process with matrix below
        # 1 is MLB, 7 is Dead
        """
            [,1] [,2] [,3] [,4] [,5] [,6] [,7]
        [1,] 1.00 0.00 0.00 0.00 0.00 0.00  0.0
        [2,] 0.75 0.15 0.00 0.00 0.00 0.00  0.1
        [3,] 0.25 0.35 0.30 0.00 0.00 0.00  0.1
        [4,] 0.05 0.25 0.35 0.25 0.00 0.00  0.1
        [5,] 0.01 0.05 0.25 0.35 0.24 0.00  0.1
        [6,] 0.01 0.01 0.05 0.25 0.35 0.23  0.1
        [7,] 0.00 0.00 0.00 0.00 0.00 0.00  1.0

        """
        eta_draw = random.random()
        if self.eta == 1:
            if eta_draw < .75:
                self.eta = 0
            elif eta_draw > .9:
                self.dead = True
        elif self.eta == 2:
            if eta_draw < .25:
                self.eta = 0
            elif eta_draw < .25 + .35:
                self.eta = 1
            elif eta_draw > .9:
                self.dead = True
        elif self.eta == 3:
            if eta_draw < .05:
                self.eta = 0
            elif eta_draw < .05 + .25:
                self.eta = 1
            elif eta_draw < .05 + .25 + .35:
                self.eta = 2
            elif eta_draw > .9:
                self.dead = True
        elif self.eta == 4:
            if eta_draw < .01:
                eta_draw = 0
            elif eta_draw < .01 + .05:
                self.eta = 1
            elif eta_draw < .01 + .05 + .25:
                self.eta = 2
            elif eta_draw < .01 + .05 + .25 + .35:
                self.eta = 3
            elif eta_draw > .9:
                self.dead = True
        elif self.eta == 5:
            if eta_draw < .01:
                eta_draw = 0
            elif eta_draw < .01 + .01:
                eta_draw = 1
            elif eta_draw < .01 + .01 + .05:
                self.eta = 2
            elif eta_draw < .01 + .01 + .05 + .25:
                self.eta = 3
            elif eta_draw < .01 + .01 + .05 + .25 + .35:
                self.eta = 4
            elif eta_draw > .9:
                self.dead = True

if __name__ == "__main__":

    mets = Team("Mets", 3, "NL", [], [])

    current_year = 2019

    # Scouting data
    with open('prospect_data/mets-board-data.csv') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skips header line
        for r in reader:
            fv = int(r[7].replace("+", ""))  # future value
            pitcher = r[2] == "RHP" or r[2] == "LHP"

            pros = Prospect(int(r[8]) - current_year, fv, int(round(float(r[10]))), pitcher, name=r[0])
            mets.add_prospect(pros)

    """
    # Prints mets prospects
    for p in mets.prospects:
        print(p.name + ", FV: " + str(p.fv) + ", Age: " + str(p.age))
    """

    def test_prospect(pros):
        print(pros.name)
        print("2019. " + "FV: " + str(pros.fv) + ", ETA: " + str(2019 + pros.eta) + ", Age: " + str(pros.age))

        for y in range(5):
            pros.develop()
            if pros.eta <= 0:
                print("MLB")
                break
            elif pros.dead:
                print("Dead")
                break
            print(str(2019 + y + 1) + ". " + "FV: " + str(pros.fv) + ", ETA: " + str(2019 + 1 + y + pros.eta) + ", Age: " + str(pros.age))
    # test_prospect(mets.prospects[3])

    # Parsing baseball reference's entry for each year's contract value
    def parse_contract_year(entry):
        if entry == "":
            return None
        if "[" in entry:  # DOESN'T PROCESS OPTIONS; TODO
            return None
        if entry == "FA":
            return None
        if '$' in entry:
            # true if value is in millions, false if thousands
            millions = 'm' in entry.lower()
            num = float(entry.lower().replace("$", "").replace("m", "").replace("k", ""))
            if millions:
                num = 1_000_000 * num
            else:
                num = 1000 * num
            return {'type': 'salary', 'value': num}
        if "Pre-Arb" in entry:
            return {'type': 'pre-arb', 'value': None}
        if "Arb" in entry:
            return {'type': 'arb', 'value': None}

    with open('mets-contracts.csv') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skips header line
        for row in reader:
            payouts = []
            for year in row[7:]:
                parsed = parse_contract_year(year)
                if parsed is not None:
                    payouts.append(parsed)
            play = Player(row[0].split("\\")[1], 0, 20, False, name=row[0].split("\\")[0])
            mets.add_contract(play, payouts)

    def replace_player_helper(team, player_id, player_war, player_age, player_pos):
        # if it can't find player_id in the team, it doesn't do anything
        for existing in team.contracts:
            pobj = existing['player']
            if pobj.id == player_id:
                pobj.war = player_war
                pobj.age = player_age
                pobj.pitcher = player_pos
                return None
        print("Not found: " + str(player_id))

    with open('mets-players.csv') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skips header line
        for row in reader:
            replace_player_helper(mets, row[0].split("\\")[1], float(row[26]), int(row[1]), (int(row[13]) > 0))

    for contract in mets.contracts:
        print(contract['player'].name + ", " + str(contract['player'].war))

    print("Num contracts: " + str(len(mets.contracts)))
