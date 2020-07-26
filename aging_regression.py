import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, Normalizer
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR
import random
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import scipy
from scipy.stats import cauchy


"""

This script takes the data obtained via war_data_scraping.py and fits it to an
appropriate model. The function war_predictor is used to progress players in
the simulation based on the fitted model's prediction and a normally distributed
error term.

"""


# Loading career war data into dataframes
df = pd.read_csv('Aging Data/WAR_by_Age1.csv', converters={'WAR': eval,'Age': eval, "Games": eval})
df = df[df['Age'] != "--"]
batting_df = df[df['pitcher']==False].drop("pitcher", axis=1)
pitching_df = df[df['pitcher']==True].drop("pitcher", axis=1)


def average(list1):
    return sum(list1[-4:]) / len(list1[-4:])


def filter_data1(df, pitcher):
    df_list = []
    indexes = list(df.index)
    batting_game_cutoff = 0
    pitching_game_cutoff = 0
    if pitcher:
        game_cutoff = pitching_game_cutoff
    else:
        game_cutoff = batting_game_cutoff
    for i in indexes:
        if pitcher == df.loc[i, 'pitcher']:
            ages = df.loc[i, 'Age']
            wars = df.loc[i, 'WAR']
            games = df.loc[i, 'Games']
            start_ratio = df.loc[i, 'start_ratio']
            for j in range(1, len(games) - 1):
                if games[j] > game_cutoff and games[j + 1] > game_cutoff and games[j - 1] > game_cutoff and -8 < wars[j+1] - wars[j] < 8:
                    df_list.append({"WAR": wars[j+1], "Age": ages[j+1], "Previous War": wars[j],
                                    "Average War": average(wars[:j+1]), "ratio": start_ratio})
    if pitcher:
        return pd.DataFrame(df_list)
    else:
        return pd.DataFrame(df_list).drop('ratio', axis=1)


def filter_data(df):
    df_list = []
    indexes = list(df.index)
    for i in range(2, len(df) - 1):
        index0 = indexes[i - 1]
        index1 = indexes[i]
        index2 = indexes[i + 1]
        age2 = float(df.loc[index2, "Age"])
        war0 = float(df.loc[index0, "WAR"])
        war1 = float(df.loc[index1, "WAR"])
        war2 = float(df.loc[index2, "WAR"])
        ratio = float(df.loc[index1, "start_ratio"])
        if index1 == index2 - 1 and -8 < war2 - war1 < 8 and index0 == index1 - 1:
            df_list.append({"WAR": war2, "Age": age2, "Previous War": war1, "2yr_war": war0, "ratio": ratio})
    df = pd.DataFrame(df_list)
    df.to_csv('regression_data1.csv')
    return df


def getNeighbors(df):
    neigh = KNeighborsRegressor(n_neighbors=10)
    y = df["WAR"]
    X = df.drop("WAR", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    neigh.fit(X_train, y_train)
    print(neigh.score(X_test, y_test))
    residuals = y_train - neigh.predict(X_train)
    mu, std = norm.fit(residuals)
    return neigh, sc, mu, std


def getNeural(df):
    regr = MLPRegressor(max_iter=500, hidden_layer_sizes=(50,100,50), solver='sgd', alpha=0.05, learning_rate='constant')
    y = df["WAR"]
    X = df.drop("WAR", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    regr.fit(X_train, y_train)
    print(regr.score(X_test, y_test))
    residuals = y_train - regr.predict(X_train)
    # _, bins, _ = plt.hist(residuals, 150, density=1, alpha=0.5)
    # mu, std = scipy.stats.gamma.fit(residuals)
    # best_fit_line = scipy.stats.gamma.pdf(bins, mu, std)
    # plt.plot(bins, best_fit_line)
    # plt.title(str(mu) + str(std))
    # plt.show()
    return regr, sc, residuals


def getForest(df):
    regr = RandomForestRegressor(random_state=0, min_samples_leaf=5)
    y = df["WAR"]
    X = df.drop("WAR", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    regr.fit(X_train, y_train)
    print(regr.score(X_test, y_test))
    residuals = y_train - regr.predict(X_train)
    mu, std = norm.fit(residuals)
    return regr, sc, mu, std


def getLinear(df):
    regr = LinearRegression()
    y = df["WAR"]
    X = df.drop("WAR", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    regr.fit(X_train, y_train)
    print(regr.score(X_test, y_test))
    residuals = y_train - regr.predict(X_train)
    mu, std = norm.fit(residuals)
    return regr, sc, mu, std


def getPoly(df):
    regr = LinearRegression()
    y = df["WAR"]
    X = df.drop("WAR", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    sc = PolynomialFeatures(2)
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    regr.fit(X_train, y_train)
    print(regr.score(X_test, y_test))
    residuals = y_train - regr.predict(X_train)
    _, bins, _ = plt.hist(residuals, 150, density=1, alpha=0.5)
    mu, std = scipy.stats.norm.fit(residuals)
    best_fit_line = scipy.stats.norm.pdf(bins, mu, std)
    plt.plot(bins, best_fit_line)
    plt.title(str(mu) + str(std))
    plt.show()
    return regr, sc, mu, std


def getSVR(df):
    regr = SVR(kernel = 'rbf')
    y = df["WAR"]
    X = df.drop("WAR", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    regr.fit(X_train, y_train)
    print(regr.score(X_test, y_test))
    residuals = y_train - regr.predict(X_train)
    mu, std = norm.fit(residuals)
    return regr, sc, mu, std


def getModel(df):
    return getNeural(df)


batting = filter_data1(df, False)
pitching = filter_data1(df, True)


bat_model, scb, residualsb = getModel(batting)
pitch_model, scp, residualsp = getModel(pitching)

# test = []
# for i in range(10000):
#     test.append()
#
# plt.hist(test, bins=100)
# plt.show()



def war_predictor(age, war, average, pitching, start_ratio):
    if pitching:
        return pitch_model.predict(scp.transform([[age, war, average, start_ratio]]))[0] + random.choice(list(residualsp))
    else:
        return bat_model.predict(scb.transform([[age, war, average]]))[0] + random.choice(list(residualsb))


# parameter_space = {
#     'hidden_layer_sizes': [(50,50,50), (50,100,50), (100,)], + np.random.normal(mub, stdb)
#     'solver': ['sgd', 'adam'], + np.random.normal(mup, stdp)
#     'alpha': [0.0001, 0.05],
# }
# mlp = MLPRegressor(random_state=1, max_iter=500)
# clf = GridSearchCV(mlp, parameter_space, n_jobs=-1, cv=3)
# clf.fit(X_train2, y_train2)
# print('Best parameters found:\n', clf.best_params_)
