from team import DRAFT_PICKS, J2_SIGNINGS, PRE_ARB
from aging_regression import war_predictor_fast, average, predict_start_ratio_fast, adjust_prospect_war
from player import Player
from team import BATTER_FV_DICT, PITCHER_FV_DICT
from prospect import eta_matrix, fv_walk
import numpy as np
import multiprocessing as mp


class League:
    """

    teams: a list of team objects

    """
    def __init__(self, teams):
        self.teams = teams

    # Age all players in the league at once - for performance
    def age_players_fast(self):
        cdef list pitcher_args = []
        cdef list batter_args = []
        for team in self.teams:
            for cont in team.contracts:
                play = cont['player']
                play.age += 1
                if play.pitcher:
                    pitcher_args.append([play.age, play.wars[-1], average(play.wars), play.start_ratio])
                else:
                    batter_args.append([play.age, play.wars[-1], average(play.wars)])

        all_wars = list(war_predictor_fast(pitcher_args, batter_args))

        cdef int all_batters_index = 0
        cdef int all_pitchers_index = 0
        for team in self.teams:
            for i in range(len(team.contracts)):
                play = team.contracts[i]['player']
                if play.pitcher:
                    play.wars.append(all_wars[0][all_pitchers_index])
                    all_pitchers_index += 1
                else:
                    play.wars.append(all_wars[1][all_batters_index])
                    all_batters_index += 1

    def age_prospects_fast(self):

        total_num_prospects = sum([len(x.prospects) for x in self.teams])
        # FV Draw
        fv_draws_total = np.random.choice(np.arange(-2, 3), total_num_prospects, p=fv_walk)
        # ETA Draw
        eta_draws_total = np.random.random_sample(total_num_prospects)

        cdef int prospect_index = 0
        for team in self.teams:
            num_prospects = len(team.prospects)
            for i in range(num_prospects):
                pros = team.prospects[i]
                if pros.dead:
                    continue
                
                pros.age += 1

                pros.fv = min(max(pros.fv + 5 * fv_draws_total[prospect_index], 20), 80)
                eta_draw = eta_draws_total[prospect_index]
                prospect_index += 1

                eta_sums = list()
                prev_sum = 0  # memoization
                for k in range(8):
                    prev_sum += eta_matrix[pros.eta][k]
                    eta_sums.append(prev_sum)

                if eta_draw < eta_sums[0]:
                    pros.eta = 0
                elif eta_draw < eta_sums[1]:
                    pros.eta = 1
                elif eta_draw < eta_sums[2]:
                    pros.eta = 2
                elif eta_draw < eta_sums[3]:
                    pros.eta = 3
                elif eta_draw < eta_sums[4]:
                    pros.eta = 4
                elif eta_draw < eta_sums[5]:
                    pros.eta = 5
                elif eta_draw < eta_sums[6]:
                    pros.eta = 6
                else:
                    pros.dead = True
            
            eta_0s = list(filter(lambda x: x.eta == 0, team.prospects))
            num_new_mlbers = len(eta_0s)
            if num_new_mlbers > 0:
                new_wars = [[PITCHER_FV_DICT[pros.fv]] if pros.pitcher else [BATTER_FV_DICT[pros.fv]] for pros in eta_0s]
                startses = predict_start_ratio_fast(new_wars)
                for i in range(num_new_mlbers):
                    pros = eta_0s[i]
                    new_id = pros.name
                    new_war = new_wars[i][0]
                    starts = min(startses[i], 1)
                    new_war = [adjust_prospect_war(new_war, pros.age, pros.pitcher)]
                    new_player = Player(new_id, new_war, pros.age, pros.pitcher, starts, name=pros.name,
                                        sim_grown=True)

                    # Three years of pre-arb, three years of arb
                    new_payouts = [{'type': 'pre-arb', 'value': PRE_ARB}, {'type': 'pre-arb', 'value': PRE_ARB},
                                    {'type': 'pre-arb', 'value': PRE_ARB}, {'type': 'arb', 'value': None},
                                    {'type': 'arb', 'value': None}, {'type': 'arb', 'value': None}]

                    team.contracts.append({'player': new_player, 'payouts': new_payouts})
            
            team.prospects = list(filter(lambda x: x.eta != 0 and not x.dead, team.prospects))


    def run_year_fast(self):
        self.age_players_fast()  # Ages players by a year, gets new WAR value
        self.age_prospects_fast()  # Ages prospects, develops by a year, adds to MLB if needed
        for team in self.teams:
            team.add_player_variance()  # Adds in-season noise

            if team.max_payroll is None:
                team.max_payroll = team.get_contract_values()

            team.record_year()  # Collects WAR for players, prospects, and FA
            team.update_contracts()  # Progresses contracts by a year

            # Assumes each team picks 5 players - only looking for top prospects here (simulating Fangraphs' The Board)
            team.add_draft_picks(DRAFT_PICKS)
            # Based on analysis, draft prospects outnumber J2 signings close to 1.7-1
            team.add_ifas(J2_SIGNINGS)

    
    def run_years(self, num_years):
        for _ in range(num_years):
            self.run_year_fast()
