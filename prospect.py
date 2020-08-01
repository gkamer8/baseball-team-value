import random

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
        # -2    -1    0    1    2
        # .15 .30  .50  .04 .01
        fv_draw = random.random()
        if fv_draw < .15:
            self.fv = max(self.fv - 10, 20)
        elif fv_draw < .15 + .30:
            self.fv = max(self.fv - 5, 20)
        elif fv_draw < .15 + .30 + .50:
            pass
        elif fv_draw < .15 + .30 + .50 + .04:
            self.fv = min(self.fv + 5, 80)
        else:
            self.fv = min(self.fv + 10, 80)

        # Evolve ETA
        # Markov process with matrix below
        # 1 is MLB, 7 is Dead
        """
            [,1] [,2] [,3] [,4] [,5] [,6] [,7]
        [1,] 1.00 0.00 0.00 0.00 0.00 0.00  0.0
        [2,] 0.70 0.15 0.00 0.00 0.00 0.00  0.15
        [3,] 0.20 0.35 0.30 0.00 0.00 0.00  0.15
        [4,] 0.05 0.20 0.35 0.25 0.00 0.00  0.15
        [5,] 0.01 0.05 0.20 0.35 0.24 0.00  0.15
        [6,] 0.01 0.01 0.05 0.20 0.35 0.23  0.15
        [7,] 0.00 0.00 0.00 0.00 0.00 0.00  1.0

        """
        eta_draw = random.random()
        if self.eta == 1:
            if eta_draw < .70:
                self.eta = 0
            elif eta_draw > .85:
                self.dead = True
        elif self.eta == 2:
            if eta_draw < .20:
                self.eta = 0
            elif eta_draw < .25 + .35:
                self.eta = 1
            elif eta_draw > .85:
                self.dead = True
        elif self.eta == 3:
            if eta_draw < .05:
                self.eta = 0
            elif eta_draw < .05 + .25:
                self.eta = 1
            elif eta_draw < .05 + .25 + .35:
                self.eta = 2
            elif eta_draw > .85:
                self.dead = True
        elif self.eta == 4:
            if eta_draw < .01:
                eta_draw = 0
            elif eta_draw < .01 + .05:
                self.eta = 1
            elif eta_draw < .01 + .05 + .20:
                self.eta = 2
            elif eta_draw < .01 + .05 + .20 + .35:
                self.eta = 3
            elif eta_draw > .85:
                self.dead = True
        elif self.eta == 5:
            if eta_draw < .01:
                eta_draw = 0
            elif eta_draw < .01 + .01:
                eta_draw = 1
            elif eta_draw < .01 + .01 + .05:
                self.eta = 2
            elif eta_draw < .01 + .01 + .05 + .20:
                self.eta = 3
            elif eta_draw < .01 + .01 + .05 + .20 + .35:
                self.eta = 4
            elif eta_draw > .85:
                self.dead = True
