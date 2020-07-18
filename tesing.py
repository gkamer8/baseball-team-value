import csv
import random
from scipy.stats import norm
import matplotlib.pyplot as plt
import numpy as np
from aging_regression import war_predictor
from aging import age_bucket_mapper, war_bucket_mapper
import pandas as pd

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
        tmp2 = self.previous_war
        self.war = war_predictor(self.age, self.war, self.previous_war, self.prevprev_war)
        self.previous_war = tmp
        self.prevprev_war = tmp2
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
for j in range(1):
    player1 = Player(8.6, 0, 0, 20.0)
    player1.progress_year()
    for i in range(20):
        if player1.get_retired() or player1.get_out():
            data1.append(player1.print1())
            print(i)
            break
        else:
            data.append(player1.get_war()[0])
            data2.append(player1.get_prevwar())
            player1.progress_year()
        if i == 19:
            print("made it")
            data1.append(player1.print1())
print(data)
# print(data2)
# mu, std = norm.fit(data)
#
# # Plot the histogram.
# plt.hist(data, bins=100, density=True, alpha=0.6, color='g')
#
# # Plot the PDF.
# xmin, xmax = plt.xlim()
# x = np.linspace(xmin, xmax, 100)
# p = norm.pdf(x, mu, std)
# title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
# plt.title(title)
#
# plt.show()
# #
# #
# print(data)

# [5.9772988164517535, 5.115640738224641, 6.176086022685363, 6.010856403735656, 6.071251774959499, 5.831671196002827, 5.478261723150831, 5.1967595141012035, 4.928558192698196, 4.6543670593371775, 4.505872486907144, 4.189892286694719, 3.88572799606487, 3.7030399636446347, 3.5308955554638497, 3.421987350187303, 3.3399077027529374, 3.2829004332891336, 3.0516925014434197, 2.949300377290087]