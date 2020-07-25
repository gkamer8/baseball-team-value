from aging_regression import war_predictor, average


class Player:
    def __init__(self, id, wars, age, position, starts, name=""):
        self.wars = wars
        self.age = age
        self.pitcher = position
        self.id = id  # baseball reference id
        self.name = name
        self.starts = starts

    def progress(self):
        self.age += 1
        self.wars.append(war_predictor(self.age, self.wars[-1], average(self.wars), self.pitcher, self.starts))


    def get_war(self):
        return self.wars[-1]