import csv
import random
from aging import batting_models, pitching_models, age_bucket_mapper, war_bucket_mapper
from player import Player
from team import Team
from prospect import Prospect
import numpy as np

aging_batters, aging_pitchers = batting_models, pitching_models


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
