from data import load_data, team_names
import matplotlib.pyplot as plt
import numpy as np
from sklearn import linear_model
import statistics
import math
import scipy.stats as stats
import math
import csv

if __name__ == "__main__":

    data = load_data()

    # Gets team WAR from data using team ID in playoff results
    def get_war(tid):
        for d in data:
            if d['year'] == int(tid[:4]) and d['name'] == tid[5:]:
                return d['war']
        return -1

    playoff_results = dict()  # dictionary linking team id (i.e., 2015_NYM), war, and playoff series wins
    for t in team_names:
        for y in range(2000, 2020):
            war = get_war(str(y) + "_" + t)
            playoff_results[str(y) + "_" + t] = {"wins": 0, "appearances": 0, "war": war}

    with open('Playoffs/PlayoffResults.csv') as csvfile:

        reader = csv.reader(csvfile)
        next(reader)
        for r in reader:
            year = r[0]
            winner_team_id = year + "_" + r[1]
            loser_team_id = year + "_" + r[2]

            if r[3] != "NLWC" and r[3] != "ALWC":
                playoff_results[winner_team_id]['wins'] += 1
                playoff_results[winner_team_id]['appearances'] += 1

                playoff_results[loser_team_id]['appearances'] += 1

                playoff_results[winner_team_id]['war'] = get_war(winner_team_id)
                playoff_results[loser_team_id]['war'] = get_war(loser_team_id)

    # Of teams to make the divisional round, create logistic regression between regular season WAR and WS outcome

    x = []  # WAR values
    y = []  # 1 if WS is won

    for t in playoff_results:
        if playoff_results[t]['appearances'] > 0:
            x.append(playoff_results[t]['war'])
            if playoff_results[t]['wins'] == 3:
                y.append(1)
            else:
                y.append(0)

    x = np.array(x).reshape(-1, 1)
    y = np.array(y).reshape(-1, 1)

    regr = linear_model.LogisticRegression()
    regr.fit(x, y)

    print(regr.coef_)
    print(regr.intercept_)

    domain = np.linspace(30, 75, 100).reshape(-1, 1)
    y_pred = []
    for d in domain:
        y_pred.append(regr.predict_proba([d])[0][1])

    plt.scatter(x, y)
    plt.plot(domain, y_pred, color="red", label="y = 1 / (1 + exp(-(-4.14 + 0.0472x)))")

    plt.ylabel("Probability")
    plt.xlabel("Regular Season WAR")
    plt.legend()

    plt.show()
