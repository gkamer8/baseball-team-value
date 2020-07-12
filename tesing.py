import csv
import random
from scipy.stats import norm
import matplotlib.pyplot as plt
import numpy as np
from aging_regression import mean, std
from aging import age_bucket_mapper, war_bucket_mapper

class Player:

    def __init__(self, war, previous_war, prevprev_war, age):
        self.war = war
        self.previous_war = previous_war
        self.prevprev_war = prevprev_war
        self.age = age
        self.careerWar = 0
        self.retired = False
        self.outofLeague = False

    def progress_year(self):
        self.age += 1
        if not self.outofLeague or self.retired:
            self.careerWar += self.war
        age_bucket = age_bucket_mapper(self.age)
        tmp = self.war
        self.war = random.normalvariate(mean(age_bucket, self.war, self.previous_war, self.prevprev_war), std)
        self.previous_war = tmp
        if not self.retired and (random.normalvariate(0, 2) + 5*self.war + (30 - self.age) < -10):
            self.retired = True
            print("retiree")
        if not self.outofLeague and not self.retired and (random.normalvariate(0, 1) + 2*self.war < -3):
            self.outofLeague = True
            print("Out of League")



    def print(self):
        print("Age: " + str(self.age))
        print("War: " + str(self.war))

    def print1(self):
        return self.careerWar

    def get_age(self):
        return self.age

    def get_war(self):
        return self.war

    def get_prevwar(self):
        return self.previous_war

    def get_prevprevwar(self):
        return self.prevprev_war

    def get_retired(self):
        return self.retired

    def get_out(self):
        return self.outofLeague


data = []
data1 = []
data2 = []
# for i in range(18, 50):
#     data[str(i)] = []
for j in range(10000):
    player1 = Player(8, 0, 0, 20)
    player1.progress_year()
    for i in range(1):
        if player1.get_retired() or player1.get_out():
            data1.append(player1.print1())
            print(i)
            break
        else:
            data.append(player1.get_war())
            data2.append(player1.get_prevwar())
            player1.progress_year()
        if i == 19:
            print("made it")
            data1.append(player1.print1())
# print(data)
# print(data2)
mu, std = norm.fit(data)

# Plot the histogram.
plt.hist(data, bins=100, density=True, alpha=0.6, color='g')

# Plot the PDF.
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)
title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
plt.title(title)

plt.show()
#
#
# print(data)