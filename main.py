import argparse
import multiprocessing as mp
import os
from load_all_teams import create_team, team_list
import time
import json
from copy import deepcopy
from parse_sims import print_first_year_payrolls, print_average_championships, print_average_sources, print_average_wl, export_championships_per_team_per_year, export_team_values
from league import League

parser = argparse.ArgumentParser(description='Value franchises by discounting championships')

parser.add_argument('-n', type=int, nargs='?', default=15,
                    help='number of sims to run')

parser.add_argument('-o', type=str, nargs='?', default='values.csv',
                    help='path of csv outfile')

parser.add_argument('-s', type=str, nargs='?',
                    help='folder for sim run json outfiles')

parser.add_argument('-y', type=int, nargs='?', default=15,
                    help='number of years to simulate')

parser.add_argument('-r', type=float, nargs='?', default=.25,
                    help='discount rate for championships')

parser.add_argument('--discount', action='store_true',
                    help="don't re-run sims but use currently set discount rate")

parser.add_argument('--sources', action='store_true',
                    help='print sources of WAR per year')

parser.add_argument('--winloss', action='store_true',
                    help='print yearly WL percentage')

parser.add_argument('--champs', action='store_true',
                    help='print yearly total championship probability')

parser.add_argument('--payrolls', action='store_true',
                    help='print first year max payrolls')

parser.add_argument('--champs_table', type=str, nargs='?', const='champs_table.csv',
                    help='export csv of championship probability per team per year')


args = parser.parse_args()

DEFAULT_SIM_PATH = 'simulations'

DEFAULT_TEAMS = [create_team(team) for team in team_list]

# Create folder for sims if needed
if args.s is None:
    args.s = DEFAULT_SIM_PATH
    if not os.path.exists(DEFAULT_SIM_PATH):
        try:
            os.mkdir(DEFAULT_SIM_PATH)
        except OSError:
            print("Creation of the default sim directory failed")


def sim_wrapper(func):
    def wrapper(filename):
        tic = time.perf_counter()
        print(f"Running sim for {filename}...")
        func(filename)
        print(f"Sim complete in {time.perf_counter() - tic:0.3f} seconds")
    return wrapper


# Creates JSON file with records for each year of the sim stored by team
@sim_wrapper
def sim_run(filename, teams=DEFAULT_TEAMS):
    team_records = dict()

    teams = deepcopy(teams)
    league = League(teams)

    num_years = args.y

    league.run_years(num_years)
    
    for team in league.teams:
        team_records[team.name] = team.records

    with open(f"{args.s}/{filename}", "w") as outfile:
        json.dump({'teams': team_records}, outfile)

# If the discount flag is activated, new sims aren't run, but export_team values redos the discount
if not args.discount:
    for i in range(args.n):
        sim_run(f'run{i}.json')
fnames = [f'{args.s}/run{i}.json' for i in range(args.n)]

if args.sources:
    print_average_sources(fnames)

if args.winloss:
    print_average_wl(fnames)

if args.champs:
    print_average_championships(fnames)

if args.payrolls:
    print_first_year_payrolls(fnames[0])

if args.champs_table is not None:
    export_championships_per_team_per_year(fnames, outfile=args.champs_table)
    print(f'Finished exporting championships by year to {args.champs_table}.')

export_team_values(fnames, outfile=args.o, discount=args.r)
print(f'Finished exporting values to {args.o}.')
