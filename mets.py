import csv

class Team:

    """

    A team has:
    1. name (string) | Name of MLB team
    2. division (int) | MLB division - 6 total
    3. league (string - NL or AL) | MLB league
    4. contracts (list of dictionaries with -) | All the existing contracts of the team
        a) player (Player object) | Player of the contract
        b) salaries (list of ints) | Dollar figures of salary for each year
    5. prospects (list of Prospect objects) | Farm system
    6. num_champs (int) | Number of WS wins during run
    7. records (list of dictionaries with -) | Season outcomes
        a) wins (int)
        b) losses (int)
        c) div_place (int)
        d) outcome (string - empty or WC or DS or CS or WS)

    """
    
    def __init__(self, name, division, league):
        self.name = name
        self.division = division
        self.league = league


class Player:
    
    def __init__(self):
        pass

class Prospect:

    def __init__(self):
        pass

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


    