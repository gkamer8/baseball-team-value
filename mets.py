import csv
import random

class Team:

    """

    A team has, for variables:
    1. name (string) | Name of MLB team
    2. division (int) | MLB division - 6 total
    3. league (string - NL or AL) | MLB league
    4. contracts (list of dictionaries with -) | All the existing contracts of the team
        a) player (Player object) | Player of the contract
        b) salaries (list of ints) | Dollar figures of salary for each year
    5. prospects (list of Prospect objects) | Farm system
    6. records (list of dictionaries with -) | Season outcomes
        a) wins (int)
        b) losses (int)
        c) div_place (int)
        d) outcome (string - empty or WC or DS or CS or WS)

    """
    
    def __init__(self, name, division, league, contracts, prospects):
        self.name = name
        self.division = division
        self.league = league

        self.contracts = contracts
        self.prospects = prospects

        self.records = []

class Player:
    
    def __init__(self):
        pass

# Inherits Player?
class Prospect:

    """

    A prospect has, for variables:
    1. eta - (int) | Estimated time of arrival - # of years
    2. fv - (int) | Future value from Fangraphs
    3. dead - (bool) | Is the player irrecovably injured/otherwise hopeless
    4. age - (int) | Age of player

    """

    def __init__(self, eta, fv, age):
        self.eta = eta
        self.fv = fv
        self.dead = False
        self.age = age

    # Develop one year
    # Process is loosely based on historical data from Fangraphs scouting results
    def develop(self):
        self.age += 1  # Prospect ages 1 year

        # Evolve FV
        # Random walk with probabilities below
        # -2    -1    0    1    2 
        # .125 .25  .35  .25 .125
        fv_draw = random.random()
        if fv_draw < .125:
            self.fv = max(self.fv - 10, 20)
        elif fv_draw < .125 + .25:
            self.fv = max(self.fv - 5, 20)
        elif fv_draw < .125 + .25 + .35:
            pass
        elif fv_draw < .125 + .25 + .35 + .25:
            self.fv = min(self.fv + 5, 80)
        else:
            self.fv = min(self.fv + 10, 80)

        # Evolve ETA
        # Markov process with matrix below
        # 1 is MLB, 7 is Dead
        """
            [,1] [,2] [,3] [,4] [,5] [,6] [,7]
        [1,] 1.00 0.00 0.00 0.00 0.00 0.00  0.0
        [2,] 0.75 0.15 0.00 0.00 0.00 0.00  0.1
        [3,] 0.25 0.35 0.30 0.00 0.00 0.00  0.1
        [4,] 0.05 0.25 0.35 0.25 0.00 0.00  0.1
        [5,] 0.01 0.05 0.25 0.35 0.24 0.00  0.1
        [6,] 0.01 0.01 0.05 0.25 0.35 0.23  0.1
        [7,] 0.00 0.00 0.00 0.00 0.00 0.00  1.0

        """
        eta_draw = random.random()
        if self.eta == 1:
            if eta_draw < .75:
                self.eta = 0
            elif eta_draw > .9:
                self.dead = True
        elif self.eta == 2:
            if eta_draw < .25:
                self.eta = 0
            elif eta_draw < .25 + .35:
                self.eta = 1
            elif eta_draw > .9:
                self.dead = True
        elif self.eta == 3:
            if eta_draw < .05:
                self.eta = 0
            elif eta_draw < .05 + .25:
                self.eta = 1
            elif eta_draw < .05 + .25 + .35:
                self.eta = 2
            elif eta_draw > .9:
                self.dead = True
        elif self.eta == 4:
            if eta_draw < .01:
                eta_draw = 0
            elif eta_draw < .01 + .05:
                self.eta = 1
            elif eta_draw < .01 + .05 + .25:
                self.eta = 2
            elif eta_draw < .01 + .05 + .25 + .35:
                self.eta = 3
            elif eta_draw > .9:
                self.dead = True
        elif self.eta == 5:
            if eta_draw < .01:
                eta_draw = 0
            elif eta_draw < .01 + .01:
                eta_draw = 1
            elif eta_draw < .01 + .01 + .05:
                self.eta = 2
            elif eta_draw < .01 + .01 + .05 + .25:
                self.eta = 3
            elif eta_draw < .01 + .01 + .05 + .25 + .35:
                self.eta = 4
            elif eta_draw > .9:
                self.dead = True

# Fangraphs FV to mean WAR

pitcher_fv_dict = {
    20: -0.1,
    30: 0.0,
    35: 0.1,
    40: 0.45,
    45: 1.35,
    50: 2.15,
    55: 3,
    60: 4.2,
    70: 6,
    80: 7
}

batter_fv_dict = {
    20: -0.1,
    30: 0.0,
    35: 0.1,
    40: 0.35,
    45: 1.15,
    50: 2,
    55: 2.9,
    60: 4.15,
    70: 6,
    80: 7
}

if __name__ == "__main__":

    # Scouting data

    with open('mets-board-data.csv') as csvfile:
        this_file = []
        reader = csv.reader(csvfile)
        next(reader)  # skips header line
        for r in reader:
            fv = int(r[7].replace("+", ""))  # future value
            pitcher = r[2] == "RHP" or r[2] == "LHP"

            if pitcher:
                mean_war = pitcher_fv_dict[fv]
            else:
                mean_war = batter_fv_dict[fv]

            print(mean_war)


    