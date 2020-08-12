import argparse
import os
from load_all_teams import create_team, team_list, copy_team
import time
import json
from parse_sims import print_first_year_payrolls, print_average_championships, print_average_sources, \
    print_average_wl, export_championships_per_team_per_year, export_team_values, export_player_table
from league import League
from multiprocessing import *

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

parser.add_argument('--player_tables', type=str, nargs='?', const='player-war',
                    help='export csvs of with player WARs for each team per year')


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


# Creates JSON file with records for each year of the sim stored by team
def sim_run(filename, teams=None):
    print(f"Running sim for {filename}...")
    tic = time.perf_counter()

    if teams is None:
        teams = DEFAULT_TEAMS

    team_records = dict()

    teams = [copy_team(team) for team in teams]
    league = League(teams)

    num_years = args.y

    league.run_years(num_years)
    
    for team in league.teams:
        team_records[team.name] = team.records

    with open(f"{filename}", "w") as outfile:
        json.dump({'teams': team_records}, outfile)

    print(f"Sim for {filename} complete in {time.perf_counter() - tic:0.3f} seconds")

fnames = [f'{args.s}/run{i}.json' for i in range(args.n)]

# If the discount flag is activated, new sims aren't run, but export_team values redoes the discount
if not args.discount:

    total_start = time.perf_counter()

    # Runs sims concurrently
    with Pool(cpu_count()) as pool:
        pool.map(sim_run, fnames)

    print(f'{args.n} sims finished in {time.perf_counter() - total_start:0.3} seconds')

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

if args.player_tables is not None:
    export_player_table(fnames, directory=args.player_tables)
    print(f'Finished exporting player WARs by year to {args.player_tables}.')

export_team_values(fnames, outfile=args.o, discount=args.r)
print(f'Finished exporting values to {args.o}.')
