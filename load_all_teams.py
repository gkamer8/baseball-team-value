from player import Player
from team import Team
from prospect import Prospect
import pandas as pd
import csv
import numpy as np
from war_wl import get_war_wl_regr
import json
import time
import random

current_year = 2019

war_wl = get_war_wl_regr()

def convert_wars_to_probabilities(war):
    return war_wl.predict([[war]])[0][0]

# Creates a team and fills it with players and prospects
def create_team(name):
    df = pd.read_csv("Full Team Data & Contracts/" + name + "_data.csv", converters={'career': eval, 'contracts': eval})
    team = Team(name, 3, "NL", [], [])
    for i in range(len(df)):
        srv = df.loc[i, 'SrvTm']
        if float(srv) > 1:
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
        num_years = 15

        for team in teams:
            team.run_years(num_years)
            team_records[team.name] = team.records

        with open(f"Sim Records/{filename}", "w") as outfile:
            json.dump({'teams': team_records}, outfile)

    # sim_run("v1.json")

    for i in range(10):
        sim_run(f'run{i}.json')

