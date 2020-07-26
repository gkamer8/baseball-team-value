import pandas as pd
import scipy
from scipy.stats import norm
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.datasets import make_regression
from sklearn.preprocessing import StandardScaler, Normalizer
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GridSearchCV
import math
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR


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
    return sum(list1) / len(list1)


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
                if games[j] > game_cutoff and games[j + 1] > game_cutoff and games[j - 1] > game_cutoff:
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


def filter_data_first_year(df):
    df_list = []
    indexes = list(df.index)
    for i in range(2, len(df) - 1):
        index0 = indexes[i - 1]
        index1 = indexes[i]
        index2 = indexes[i + 1]
        age2 = float(df.loc[index2, "Age"])
        war1 = float(df.loc[index1, "WAR"])
        war2 = float(df.loc[index2, "WAR"])
        ratio = float(df.loc[index1, "start_ratio"])
        if index1 == index2 - 1 and -8 < war2 - war1 < 8 and index0 != index1 - 1:
            df_list.append({"WAR": war2, "Age": age2, "Previous War": war1, "ratio": ratio})
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
    return neigh, sc


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
    return regr, sc, residuals


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
    return regr, sc


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
    mu, std = norm.fit(residuals)
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
    return regr, sc


def getModel(df):
    return getPoly(df)


# batting1 = filter_data_first_year(batting_df).drop("ratio", axis=1).dropna(axis=0)
# batting2 = filter_data(batting_df).drop("ratio", axis=1).dropna(axis=0)
# pitching1 = filter_data_first_year(pitching_df).dropna(axis=0)
# pitching2 = filter_data(pitching_df).dropna(axis=0)
# print(batting1.head())
# start_pitching1 = filter_data_first_year(starting_pitchers).dropna(axis=0)
# start_pitching2 = filter_data(starting_pitchers).dropna(axis=0)
# relief_pitching1 = filter_data_first_year(relief_pitchers).dropna(axis=0)
# relief_pitching2 = filter_data(relief_pitchers).dropna(axis=0)


batting = filter_data1(df, False)
pitching = filter_data1(df, True)

bat_model, scb, mub, stdb = getModel(batting)
print(mub, stdb)
pitch_model, scp, mup, stdp = getModel(pitching)
print(mup, stdp)

def war_predictor(age, war, average, pitching, start_ratio):
    if pitching:
        return pitch_model.predict(scp.transform([[age, war, average, start_ratio]]))[0]
    else:
        return bat_model.predict(scb.transform([[age, war, average]]))[0]

# def war_predictor1_year_b(age, war1): + np.random.normal(mub, stdb)
#     return batt1_model.predict(sc1.transform([[age, war1]])) + np.random.normal(mup, stdp)

# batt1_model, sc1, residualsb1 = getModel(batting1)
# def war_predictor1_year_b(age, war1):
#     return batt1_model.predict(sc1.transform([[age, war1]]))
#
#
# batt2_model, sc2, residualsb2 = getModel(batting2)
# def war_predictor2_years_b(age, war1, war2):
#     return batt2_model.predict(sc2.transform([[age, war1, war2]]))
#
#
# # mu, std = norm.fit(residualsb2)
# # print(mu, std)
# # n, bins, patches = plt.hist(residualsb2, bins=100)
# # plt.show()
#
# pitch1_model, sc3, residualsrp1 = getModel(pitching1)
# def war_predictor1_year_p(age, war1, ratio):
#     return pitch1_model.predict(sc3.transform([[age, war1, ratio]]))
#
#
# pitch2_model, sc4, residualsrp2 = getModel(pitching2)
# def war_predictor2_years_p(age, war1, war2, ratio):
#     return pitch2_model.predict(sc4.transform([[age, war1, war2, ratio]]))


# parameter_space = {
#     'hidden_layer_sizes': [(50,50,50), (50,100,50), (100,)],
#     'solver': ['sgd', 'adam'],
#     'alpha': [0.0001, 0.05],
# }
# mlp = MLPRegressor(random_state=1, max_iter=500)
# clf = GridSearchCV(mlp, parameter_space, n_jobs=-1, cv=3)
# clf.fit(X_train2, y_train2)
# print('Best parameters found:\n', clf.best_params_)
