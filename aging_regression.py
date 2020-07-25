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


# Loading career war data into dataframes
batting_df = pd.read_csv('Aging Data/Batters_WAR_by_Age.csv')
pitching_df = pd.read_csv('Aging Data/Pitchers_WAR_by_Age.csv')


def parse_data(df):
    df_list = 0
    for i in range(2, len(df) - 1):
        age0 = float(df.loc[i - 1, "Age"])
        age1 = float(df.loc[i, "Age"])
        age2 = float(df.loc[i + 1, "Age"])
        war0 = float(df.loc[i - 1, "WAR"])
        war1 = float(df.loc[i, "WAR"])
        war2 = float(df.loc[i + 1, "WAR"])
        if age1 == age2 - 1 and -8 < war2 - war1 < 8 and age1 == 21:
            df_list += war2 - war1
    return df_list


def filter_data(df):
    df_list = []
    for i in range(2, len(df) - 1):
        age0 = float(df.loc[i - 1, "Age"])
        age1 = float(df.loc[i, "Age"])
        age2 = float(df.loc[i + 1, "Age"])
        war0 = float(df.loc[i - 1, "WAR"])
        war1 = float(df.loc[i, "WAR"])
        war2 = float(df.loc[i + 1, "WAR"])
        if age1 == age2 - 1 and -8 < war2 - war1 < 8 and age0 == age1 - 1:
            df_list.append({"WAR": war2 - war1, "Age": age2, "Previous War": war1, "2yr_war": war0})
    df = pd.DataFrame(df_list)
    df.to_csv('regression_data1.csv')
    return df


def filter_data_first_year(df):
    df_list = []
    for i in range(2, len(df) - 1):
        age0 = float(df.loc[i - 1, "Age"])
        age1 = float(df.loc[i, "Age"])
        age2 = float(df.loc[i + 1, "Age"])
        war1 = float(df.loc[i, "WAR"])
        war2 = float(df.loc[i + 1, "WAR"])
        if age1 == age2 - 1 and -8 < war2 - war1 < 8 and math.isnan(age0):
            df_list.append({"WAR": war2 - war1, "Age": age2, "Previous War": war1})
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
    regr = MLPRegressor(random_state=1, max_iter=500, hidden_layer_sizes=(50,100,50), solver='sgd', alpha=0.05, learning_rate='adaptive')
    y = df["WAR"]
    X = df.drop("WAR", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    regr.fit(X_train, y_train)
    print(regr.score(X_test, y_test))
    return regr, sc


def getForest(df):
    regr = RandomForestRegressor(max_depth=2, random_state=0)
    y = df["WAR"]
    X = df.drop("WAR", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    regr.fit(X_train, y_train)
    print(regr.score(X_test, y_test))
    return regr, sc


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
    return regr, sc


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


batting1 = filter_data_first_year(batting_df).dropna(axis=0)
batting2 = filter_data(batting_df).dropna(axis=0)
pitching1 = filter_data_first_year(pitching_df).dropna(axis=0)
pitching2 = filter_data(pitching_df).dropna(axis=0)


batt1_model, sc1 = getModel(batting1)
def war_predictor1_year_b(age, war1):
    return batt1_model.predict(sc1.transform([[age, war1]]))


batt2_model, sc2 = getModel(batting2)
def war_predictor2_years_b(age, war1, war2):
    return batt2_model.predict(sc2.transform([[age, war1, war2]]))


pitch1_model, sc3 = getModel(pitching1)
def war_predictor1_year_p(age, war1):
    return pitch1_model.predict(sc3.transform([[age, war1]]))


pitch2_model, sc4 = getModel(pitching2)
def war_predictor2_years_p(age, war1, war2):
    return pitch2_model.predict(sc4.transform([[age, war1, war2]]))


# parameter_space = {
#     'hidden_layer_sizes': [(50,50,50), (50,100,50), (100,)],
#     'solver': ['sgd', 'adam'],
#     'alpha': [0.0001, 0.05],
# }
# mlp = MLPRegressor(random_state=1, max_iter=500)
# clf = GridSearchCV(mlp, parameter_space, n_jobs=-1, cv=3)
# clf.fit(X_train2, y_train2)
# print('Best parameters found:\n', clf.best_params_)