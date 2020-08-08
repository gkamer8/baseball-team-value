from player import Player
from team import Team
from prospect import Prospect
import pandas as pd
import csv
import random

current_year = 2019


# Creates a team and fills it with players and prospects
def create_team(name):
    df = pd.read_csv("Full Team Data & Contracts/" + name + "_data.csv", converters={'career': eval, 'contracts': eval})
    team = Team(name, 3, "NL", [], [])  # note: division and leage are currently unused
    for i in range(len(df)):
        srv = df.loc[i, 'SrvTm']
        if float(srv) > .045 and i < 32:  # exeeded rookie limits and is in the top of the roster
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
            pitcher = r[2] == "RHP" or r[2] == "LHP"
            eta = int(r[8]) - current_year

            pros = Prospect(eta, fv, int(round(float(r[10]))), pitcher, name=r[0])
            new_contracts = []
            for contract in team.contracts:
                if contract['player'].name != pros.name:
                    new_contracts.append(contract)
            team.contracts = new_contracts
            team.add_prospect(pros)

        # Add 2020 july 2nd signings
        team.add_ifas(random.randint(3, 4))

    return team


team_list = ['diamondbacks', 'braves', 'orioles', 'redsox', 'cubs', 'whitesox', 'reds', 'indians', 'rockies',
             'tigers', 'astros', 'royals', 'angels', 'dodgers', 'marlins', 'brewers', 'twins', 'mets',
             'yankees', 'athletics', 'phillies', 'pirates', 'padres', 'giants', 'mariners', 'cardinals',
             'rays', 'rangers', 'bluejays', 'nationals']
team_list1 = ['dodgers']
