from player import Player
from team import Team
from prospect import Prospect
import pandas as pd
import csv

current_year = 2019

injured_list = pd.read_csv('injured-july22-august12.csv')
# Clean
for i in range(len(injured_list)):
    try:
        injured_list['Name'][i] = injured_list['Name'][i][:injured_list['Name'][i].index('\\')]
    except ValueError:
        pass

# Creates a team and fills it with players and prospects
def create_team(name):
    df = pd.read_csv("Full Team Data & Contracts/" + name + "_data.csv", converters={'career': eval, 'contracts': eval})
    team = Team(name, 3, "NL", [], [])  # note: division and leage are currently unused
    for i in range(len(df)):
        srv = df.loc[i, 'SrvTm']

        if float(srv) >= 0.100 and len(team.contracts) < 36:  # Gets rid of AAAA players and some duplicate prospects
            wars = df.loc[i, 'career']
            payouts = df.loc[i, 'contracts']
            player_name = df.loc[i, 'Name'].split("\\")

            injured_to_start = player_name[0] in list(injured_list['Name'])

            age = df.loc[i, 'Age']
            position = df.loc[i, 'pitcher']
            starts = df.loc[i, 'start_ratio']
            play = Player(player_name[1], wars, age, position, starts, player_name[0], injured_to_start=injured_to_start)
            team.add_contract(play, payouts)
    with open('prospect_data/' + name + '-board-data.csv') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skips header line

        for r in reader:
            fv = int(r[7].replace("+", ""))  # future value
            pitcher = r[2] == "RHP" or r[2] == "LHP"
            eta = int(r[8]) - current_year

            pros = Prospect(eta, fv, int(round(float(r[10]))), pitcher, name=r[0])
            # Get rid of duplicate prospects from contracts
            team.contracts = list(filter(lambda cont: cont['player'].name != pros.name, team.contracts))
            team.add_prospect(pros)

        # Add 2020 july 2nd signings
        team.add_ifas(3)

    return team


team_list = ['diamondbacks', 'braves', 'orioles', 'redsox', 'cubs', 'whitesox', 'reds', 'indians', 'rockies',
             'tigers', 'astros', 'royals', 'angels', 'dodgers', 'marlins', 'brewers', 'twins', 'mets',
             'yankees', 'athletics', 'phillies', 'pirates', 'padres', 'giants', 'mariners', 'cardinals',
             'rays', 'rangers', 'bluejays', 'nationals']


# For performance reasons, to replace deep_copy
# Should be updated if attributes of objects change
def copy_team(team):
    new_team = Team(team.name, team.division, team.league, [], [])
    for pros in team.prospects:
        new_team.prospects.append(Prospect(pros.eta, pros.fv, pros.age, pros.pitcher, pros.name))
    for cont in team.contracts:
        play = cont['player']
        new_team.contracts.append({'player': Player(play.id, list(play.wars), play.age, play.pitcher,
                                                    play.start_ratio, play.name, play.sim_grown,
                                                    play.injured_to_start),
                                   'payouts': list(cont['payouts'])})
    return new_team
