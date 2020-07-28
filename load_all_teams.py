from player import Player
from team import Team
from prospect import Prospect
import pandas as pd
import csv
import numpy as np

current_year = 2019


def parse_contract_year(entry):
    if entry == "":
        return None
    if "[" in entry:  # DOESN'T PROCESS OPTIONS; TODO
        return None
    if entry == "FA":
        return None
    if "Arb" in entry:
        return {'type': 'arb', 'value': None}
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


# Creates a team and fills it with players and prospects
def create_team(name):
    df = pd.read_csv("Full Team Data/" + name + "_data.csv", converters={'career': eval})
    team = Team(name, 3, "NL", [], [])
    for i in range(len(df)):
        wars = df.loc[i, 'career']
        payouts = []
        for year in df.iloc[i][8:-1]:
            parsed = parse_contract_year(str(year))
            if parsed is not None:
                payouts.append(parsed)
        player_name = df.loc[i, 'Name'].split("\\")
        age = df.loc[i, 'Age']
        position = df.loc[i, 'pitcher']
        starts = df.loc[i, 'start_ratio']
        play = Player(player_name[1], wars, age, position, starts, player_name[0])
        team.add_contract(play, payouts)

    # with open('prospect_data/' + name + '-board-data.csv') as csvfile:
    #     reader = csv.reader(csvfile)
    #     next(reader)  # skips header line
    #     for r in reader:
    #         fv = int(r[7].replace("+", ""))  # future value
    #         pitcher = r[2] == "RHP" or r[2] == "LHP"
    #
    #         pros = Prospect(int(r[8]) - current_year, fv, int(round(float(r[10]))), pitcher, name=r[0])
    #         new_contracts = []
    #         for contract in team.contracts:
    #             if contract['player'].name != pros.name:
    #                 new_contracts.append(contract)
    #         team.contracts = new_contracts
    #         team.add_prospect(pros)
    return team



team_list = ['diamondbacks', 'braves', 'orioles', 'redsox', 'cubs', 'whitesox', 'reds', 'indians', 'rockies',
             'tigers', 'astros', 'royals', 'angels', 'dodgers', 'marlins', 'brewers', 'twins', 'mets',
             'yankees', 'athletics', 'phillies', 'pirates', 'padres', 'giants', 'mariners', 'cardinals',
             'rays', 'rangers', 'bluejays', 'nationals']
team_list1 = ['dodgers']
#
teams = []
for team in team_list1:
    teams.append(create_team(team))

team_names = []
team_wars = []
for team in teams:
    print(team.name)
    for i in range(5):
        team.run_year()
    for contract in team.contracts:
        print(contract['player'].name + ", " + str(contract['player'].wars[-1]))
    team_names.append(team.name)
    team_wars.append(((60 * team.get_team_war())/162))

df = pd.DataFrame(list(zip(team_names, team_wars)),
               columns =['Name', 'WAR'])
df = df.sort_values(by='WAR', ascending=False)
df.to_csv('1_yearprojectionsv2.csv')

# rangers = create_team('rangers')
# rangers.run_year()
# for contract in rangers.contracts:
#     print(contract['player'].name + ", " + str(contract['player'].wars[-1]))
