import random
import numpy as np

class Prospect:

    """

    A prospect has, for variables:
    1. eta - (int) | Estimated time of arrival - # of years
    2. fv - (int) | Future value from Fangraphs
    3. dead - (bool) | Is the player irrecovably injured/otherwise hopeless
    4. age - (int) | Age of player
    5. pitcher - (bool) | Whether or not the prospect is a pitcher
    6. name - (string) | Optional name of prospect

    """

    def __init__(self, eta, fv, age, pitcher, name=""):
        self.eta = eta
        self.fv = fv
        self.dead = False
        self.age = age
        self.pitcher = pitcher

        self.name = name

    # Develop one year
    # Process is loosely based on historical data from Fangraphs scouting results
    def develop(self):
        self.age += 1  # Prospect ages 1 year

        # Evolve FV
        # Random walk with probabilities below
        #           -2     -1      0      1      2
        fv_walk = [.15,   .25,   .50,   .09,   .01]
        fv_draw = np.random.choice(5, 1, p=fv_walk)[0]
        fv_draw -= 2
        self.fv = min(max(self.fv + fv_draw * 5, 20), 80)

        # Evolve ETA
        # Markov process with matrix below

        eta_matrix = [[] for _ in range(8)]
        #                MLB     1       2       3       4       5       6       DEAD
        eta_matrix[0] = [1.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00]  # MLB
        eta_matrix[1] = [0.75,   0.15,   0.00,   0.00,   0.00,   0.00,   0.00,   0.10]  # 1 year out
        eta_matrix[2] = [0.10,   0.80,   0.00,   0.00,   0.00,   0.00,   0.00,   0.10]  # 2 years out
        eta_matrix[3] = [0.00,   0.15,   0.75,   0.00,   0.00,   0.00,   0.00,   0.10]  # 3 years out
        eta_matrix[4] = [0.00,   0.00,   0.10,   0.75,   0.00,   0.00,   0.00,   0.15]  # 4 years out
        eta_matrix[5] = [0.00,   0.00,   0.00,   0.10,   0.75,   0.00,   0.00,   0.15]  # 5 years out
        eta_matrix[6] = [0.00,   0.00,   0.00,   0.00,   0.10,   0.75,   0.00,   0.15]  # 6 years out
        eta_matrix[7] = [0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   1.00]  # Dead

        # If a row doesn't sum to one, tell me which
        for i in range(len(eta_matrix)):
            assert round(sum(eta_matrix[i]), 5) == 1, f"Eta matrix {i} doesn't sum to one."  # round is because of an error where the sum was .999999999

        self.eta = np.random.choice(8, 1, p=eta_matrix[self.eta])[0]
        if self.eta == 7:
            self.dead = True
