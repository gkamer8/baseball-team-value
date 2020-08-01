from aging_regression import war_predictor, average, error_predictor, injury_predictor


class Player:

    """

    A player has, for variables:
    1. name (string) | Name of player
    2. id (int) | Unique id for each player
    3. wars (float list)| Career war values by year with most recent values last
    4. age (int) | Current Age of player
    5. position (bool) | True for pitchers, False for non-pitchers
    6. start_ratio (float) | Percent of games in which player will/has started at pitcher

    """

    def __init__(self, id, wars, age, position, start_ratio, name="", sim_grown=False):
        self.wars = wars
        self.age = age
        self.pitcher = position
        self.id = id  # baseball reference id
        self.name = name
        self.start_ratio = start_ratio

        self.sim_grown = sim_grown  # For record keeping – whether player comes from sim

    def progress(self):
        self.age += 1
        self.wars.append(war_predictor(self.age, self.wars[-1], average(self.wars), self.pitcher, self.start_ratio))

    def add_variance(self):
        # self.wars[-1] *= injury_predictor()
        # self.wars[-1] *= error_predictor(self.pitcher)
        self.wars[-1] += error_predictor(self.pitcher, self.wars[-1])

    def backup(self):
        self.wars[-1] = .25 * self.wars[-1]

    def get_war(self):
        return self.wars[-1]
