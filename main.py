import argparse
import os
from load_all_teams import create_team, team_list
import time
import json
from parse_sims import export_team_values, print_average_sources

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
                    help='use previous sims but change discount rate')

parser.add_argument('--sources', action='store_true',
                    help='print sources of WAR per year (use with --discount to prevent re-running sims)')

args = parser.parse_args()

DEFAULT_SIM_PATH = 'simulations'

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
def sim_run(filename):
    team_records = dict()
    teams = [create_team(team) for team in team_list]
    num_years = 15

    for team in teams:
        team.run_years(num_years)
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

export_team_values(fnames, outfile=args.o, discount=args.r)
print(f'Finished exporting values to {args.o}.')
