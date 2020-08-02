from player import Player
from team import Team
from prospect import Prospect
import pandas as pd
import csv
import numpy as np
from war_wl import get_war_wl_regr
import json
import time
from collections import Counter

current_year = 2019


war_wl = get_war_wl_regr()


def convert_wars_to_probabilities(war):
    return war_wl.predict([[war]])[0][0]


# def parse_contract_year(entry):
#     if entry == "":
#         return {'type': 'pre-arb', 'value': None}
#     if "[FA-*]" in entry or "[*]" in entry or "[Arb-*]" in entry:  # DOESN'T PROCESS OPTIONS; TODO
#         print(entry)
#         millions = 'm' in entry.lower()
#         num = float(entry.lower().replace("$", "").replace("m", "").replace("k", "").replace(" [fa-*]", "").replace(" [*]", "").replace(" [arb-*]", ""))
#         if millions:
#             num = 1_000_000 * num
#         else:
#             num = 1000 * num
#         return {'type': 'team option', 'value': num}
#     if entry == "FA":
#         return None
#     if "Arb" in entry:
#         if "$" in entry:
#             num_string = entry[entry.find("$") + 1:entry.find(")")]
#             if "M" in num_string:
#                 value = float(num_string[0:num_string.find("M")]) * 1_000_000
#                 return {'type': 'arb', 'value': value}
#             elif "k" in num_string:
#                 value = float(num_string[0:num_string.find("k")]) * 1_000
#                 return {'type': 'arb', 'value': value}
#             else:
#                 return {'type': 'arb', 'value': float(num_string)}
#         else:
#             return {'type': 'arb', 'value': None}
#     if '$' in entry:
#         # true if value is in millions, false if thousands
#         millions = 'm' in entry.lower()
#         num = float(entry.lower().replace("$", "").replace("m", "").replace("k", ""))
#         if millions:
#             num = 1_000_000 * num
#         else:
#             num = 1000 * num
#         return {'type': 'salary', 'value': num}
#     if "Pre-Arb" in entry:
#         return {'type': 'pre-arb', 'value': None}

# Creates a team and fills it with players and prospects
def create_team(name):
    df = pd.read_csv("Full Team Data & Contracts/" + name + "_data.csv", converters={'career': eval, 'contracts': eval})
    team = Team(name, 3, "NL", [], [])
    for i in range(len(df)):
        wars = df.loc[i, 'career']
        payouts = df.loc[i, 'contracts']
        player_name = df.loc[i, 'Name'].split("\\")
        age = df.loc[i, 'Age']
        position = df.loc[i, 'pitcher']
        starts = df.loc[i, 'start_ratio']
        play = Player(player_name[1], wars, age, position, starts, player_name[0])
        team.add_contract(play, payouts)
    with open('prospect_data/' + name + '-board-data.csv') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skips header line

        for r in reader:
            fv = int(r[7].replace("+", ""))  # future value
            # fv -= 5  # NERF Board prospects

            pitcher = r[2] == "RHP" or r[2] == "LHP"
            eta = int(r[8]) - current_year
            pros = Prospect(eta, fv, int(round(float(r[10]))), pitcher, name=r[0])
            new_contracts = []
            for contract in team.contracts:
                if contract['player'].name != pros.name:
                    new_contracts.append(contract)
            team.contracts = new_contracts
            team.add_prospect(pros)
    return team

team_list = ['diamondbacks', 'braves', 'orioles', 'redsox', 'cubs', 'whitesox', 'reds', 'indians', 'rockies',
             'tigers', 'astros', 'royals', 'angels', 'dodgers', 'marlins', 'brewers', 'twins', 'mets',
             'yankees', 'athletics', 'phillies', 'pirates', 'padres', 'giants', 'mariners', 'cardinals',
             'rays', 'rangers', 'bluejays', 'nationals']
team_list1 = ['dodgers']

if __name__ == "__main__":

    def sim_wrapper(func):
        def wrapper(filename):
            tic = time.perf_counter()
            print(f"Running sim for {filename}...")
            func(filename)
            print(f"Sim complete in {time.perf_counter() - tic:0.3f} seconds")
        return wrapper

    # Creates JSON file in Sim Records with records for each year of the sim stored by team
    @sim_wrapper
    def sim_run(filename):
        team_records = dict()
        teams = [create_team(team) for team in team_list]
        num_years = 30

        for team in teams:
            team.run_years(num_years)
            team_records[team.name] = team.records
        # for team in teams:
        #     for player in team.contracts:
        #         print(player['player'].name)
        #         print(player['player'].wars)
        
        with open(f"Sim Records/{filename}", "w") as outfile:
            json.dump({'teams': team_records}, outfile)
    
    sim_run('v1.json')

    """

    JARED'S CODE:

    teams = []
    for team in team_list:
        teams.append(create_team(team))

    team_names = []
    team_data = []
    for team in teams:
        team_lst = []
        team_lst.append(team.name)
        print(team.name)
        for i in range(10):
            team.run_year()
            if i == -1:
                team_lst.append(((60 * team.get_team_war()) / 162))
            else:
                team_lst.append(convert_wars_to_probabilities(team.get_team_war()))
        team_data.append(team_lst)
        for contract in team.contracts:
            print(contract['player'].name + ", " + str(contract['player'].wars[-1]))
        print(len(team.contracts))
    df = pd.DataFrame(team_data)

    skip = True
    row = []
    for column in df.columns:
        if skip:
            skip = False
            row.append("")
        else:
            row.append(df[column].sum() / 30)
    df1 = pd.DataFrame([row])
    print(df1.head())
    df = pd.concat([df, df1])

    # df = pd.DataFrame(list(zip(team_names, team_wars)),
    #                columns =['Name', 'WAR'])
    # df = df.sort_values(by='WAR', ascending=False)
    df.to_csv('1_yearprojectionsv2.csv')

    # rangers = create_team('rangers')
    # rangers.run_year()
    # for contract in rangers.contracts:
    #     print(contract['player'].name + ", " + str(contract['player'].wars[-1]))
    
    """



