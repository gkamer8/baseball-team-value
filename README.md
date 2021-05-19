# Baseball Team Value

This project is an effort to describe a Major League Baseball team's value in terms of discounted future championships. 
In order to accomplish this, we must determine the championship probability for each team in the league an arbitrary 
number of years into the future. The main feature of this repository is a model that takes as input contract and 
prospect information from every team in the league and runs simulations to determine their championship odds multiple 
years into the future. The simulation is also capable of determining the expected WAR contributions of all MLB players 
and top prospects.

## Usage

The project is designed to be run from the main.py file. Use -h for information on all of the command line arguments.

Before running the simulation, you must compile the Cython files using `python setup.py build_ext --inplace`. Note: Due to the use of fstrings, run using python3.6 or above.

A normal call of main.py will run multiple sims for each team 15 years into the future. 
After running, the program exports a file called values.csv (or whatever you passed through on the command line) containing the discounted future championship values for each team.

Be sure to use --discount if you are seeking only to interpret previous simulations without re-running them.

## Project Organization

### Data

**total.csv**: Consolidation of data for each team in each season, used for determining parameters of the championship probability function

**Batting and Pitching Folder**: Team data (including team stats and results) since 2000 (going farther back introduces problems with the expansion era and different playoff systems) as downloaded from Baseball Reference

**Playoffs**: The Playoffs folder contains a CSV with the results of every playoff round since 2012, the first year of the WC game format. This information is used for determining parameters of the championship probability function.

**Aging Data**: Individual player data to help build the models in aging_regression.py

**ETA Data**: Fangraphs' The Board data for building the prospect model

**Full Team Data and Full Team Data & Contracts**: These folders have information used in the create_team function that helps load MLB team data into the simulation when it's run.

**prospect_data**: This folder holds data that helps load teams into the simulation when it's run

**Team Data**: This folder holds data from Baseball Reference on team contracts, which is transformed into data in the other folders.

**Player Models**: Contains binary representations of the development models used in the simulation

### R

**empirical_analysis.r**: This is the main R file. It explores certain data to make decisions about constants in the model

### Python

**Scripts used to build the WAR to championship probability function:**

**data.py**: In order to load and evaluate that data, data.py provides some simple functions such as load_data(), which creates a list of teams with WAR and record, in addition to functions to determine whether teams made the playoffs and how.

**war_wl.py**: If run as main, displays graphs of the relationship between WAR and W/L%. Contains get_war_wl_regr(), which returns an sklearn regression object for the relationship between WAR and W/L%. Contains get_war_wl_resids(), which returns a list of residuals.

**ws_result_and_WAR.py**: If run as main, displays graphs of the relationship between winning the world series and regular season war among teams that make it to the divisional round.

**wl_percentage_and_division_or_wc.py**: If run as main, takes a while to display functions turning wins into playoff / division-win odds.

**Files holding classes for the simulation:**

**player.pyx**: Cython file that contains the Player class and a slow version of the player development function

**prospect.pyx**: Cython file that contains the Prospect class, prospect development constants, and a slow version of the prospect development function

**team.pyx**: Cython file that contains the team class, the function that determines a player's arbitration salary, and some important constants involving free agents and prospects

**league.pyx**: Cython file that contains league class including the fastest version of the age_players and age_prospects functions

**Outside data parsing**

**get_full_contract_data.py**: Scrapes and parses data for player contracts

**get_full_team_data.py**: Scrapes and parses data for player performance

**get_historical_war_data.py**: Scrapes and parses historical WAR data

**Files for running and interpreting the simulation:**

**aging_regression.py**: Loads and provides an interface for player development models

**parse_sims.py**: Contains important functions for interpreting sim data ex-post

**load_all_teams.py**: Contains the create_team function, which loads teams into the simulation, in addition to the copy_team function, which is used for performance reasons over copy.deepcopy.

**setup.py**: Compiles the Cython files

**main.py**: Contains a command line interface for running the entire simulation
