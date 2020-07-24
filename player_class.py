from aging_regression import war_predictor2_years_p, war_predictor1_year_p, war_predictor1_year_b, war_predictor2_years_b


class Player:
    def __init__(self, id, wars, age, position, name=""):
        self.wars = wars
        self.age = age
        self.pitcher = position
        self.id = id  # baseball reference id
        self.name = name

    def progress_year(self):
        self.age += 1
        if self.pitcher:
            if len(self.wars) > 1:
                self.wars.append((war_predictor2_years_p(self.age, self.wars[-1], self.wars[-2]))[0])
            else:
                self.wars.append((war_predictor1_year_p(self.age, self.wars[-1]))[0])
        else:
            if len(self.wars) > 1:
                self.wars.append((war_predictor2_years_b(self.age, self.wars[-1], self.wars[-2]))[0])
            else:
                self.wars.append((war_predictor1_year_b(self.age, self.wars[-1]))[0])


    def get_war(self):
        return self.wars[-1]