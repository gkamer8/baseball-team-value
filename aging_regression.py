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
import pickle


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


def prospect_conversion_data(df, pitcher):
    dct = {}
    indexes = list(df.index)
    for age in range(15, 40):
        lst = []
        for i in indexes:
            if pitcher == df.loc[i, 'pitcher']:
                ages = df.loc[i, 'Age']
                wars = df.loc[i, 'WAR']
                init_war = wars[0]
                average = sum(wars[:6]) / len(wars[:6])
                if int(ages[0]) == age and len(wars) > 5:
                    lst.append(average - init_war)
        if len(lst) > 0:
            dct[age] = sum(lst) / len(lst)
        else:
            dct[age] = 0
    print(dct)
    return dct


def pitcher_start_data(df):
    df_list = []
    indexes = list(df.index)
    batting_game_cutoff = 0
    pitching_game_cutoff = 0
    for i in indexes:
        if df.loc[i, 'pitcher'] == True:
            wars = df.loc[i, 'WAR']
            start_ratio = df.loc[i, 'start_ratio']
            df_list.append({"Average WAR": sum(wars[:6]) / len(wars[:6]), "ratio": start_ratio})
    return pd.DataFrame(df_list)


# def get_average_progressions(df):
#     averages_lst = []
#     for i in range(20, 40):
#         tmp_df = df[df['Age'] == str(i)]
#         mean = tmp_df["WAR"].mean()
#         averages_lst.append(mean)
#     return averages_lst


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
    regr = MLPRegressor(max_iter=500, hidden_layer_sizes=(50,100,50), alpha=0.05, learning_rate='constant')
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


# b_prospect_data = prospect_conversion_data(df, False)
# p_prospect_data = prospect_conversion_data(df, True)
b_prospect_adjust = 'b_prospect_adjust.sav'
p_prospect_adjust = 'p_prospect_adjust.sav'

# pickle.dump(b_prospect_data, open(b_prospect_adjust, 'wb'))
# pickle.dump(p_prospect_data, open(p_prospect_adjust, 'wb'))

adjust_batters = pickle.load(open(b_prospect_adjust, 'rb'))
adjust_pitchers = pickle.load(open(p_prospect_adjust, 'rb'))


def adjust_prospect_war(war, age, pitcher):
    if pitcher:
        return war - adjust_batters[age]
    else:
        return war - adjust_pitchers[age]


# batting = filter_data1(df, False)
# pitching = filter_data1(df, True)
# bat_model, scb, residualsb = getModel(batting)
# pitch_model, scp, residualsp = getModel(pitching)



b_model = 'b_model.sav'
p_model = 'p_model.sav'
b_sc = 'b_sc.sav'
p_sc = 'p_sc.sav'
b_resid = 'b_resid.sav'
p_resid = 'p_resid.sav'
# pickle.dump(bat_model, open(b_model, 'wb'))
# pickle.dump(pitch_model, open(p_model, 'wb'))
# pickle.dump(scb, open(b_sc, 'wb'))
# pickle.dump(scp, open(p_sc, 'wb'))
# pickle.dump(residualsb, open(b_resid, 'wb'))
# pickle.dump(residualsp, open(p_resid, 'wb'))


bat_model = pickle.load(open(b_model, 'rb'))
pitch_model = pickle.load(open(p_model, 'rb'))
scb = pickle.load(open(b_sc, 'rb'))
scp = pickle.load(open(p_sc, 'rb'))
residualsb = pickle.load(open(b_resid, 'rb'))
residualsp = pickle.load(open(p_resid, 'rb'))



def war_predictor(age, war, average, pitching, start_ratio):
    if pitching:
        return pitch_model.predict(scp.transform([[age, war, average, start_ratio]]))[0]
    else:
        return bat_model.predict(scb.transform([[age, war, average]]))[0]


def error_predictor(pitcher):
    if pitcher:
        return random.choice(list(residualsp))
    else:
        return random.choice(list(residualsb))


pitcher_starts = pitcher_start_data(df)

def getModelforStarts(df):
    regr = MLPRegressor(max_iter=1000, hidden_layer_sizes=(50, 100, 50), alpha=0.05, learning_rate='constant')
    y = df["ratio"]
    X = df.drop("ratio", axis=1)
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
    return regr, sc


# start_model, start_scaler = getModelforStarts(pitcher_starts)
st_model = 'st_model.sav'
st_scaler = 'st_scaler.sav'

# pickle.dump(start_model, open(st_model, 'wb'))
# pickle.dump(start_scaler, open(st_scaler, 'wb'))

start_model = pickle.load(open(st_model, 'rb'))
start_scaler = pickle.load(open(st_scaler, 'rb'))

def predict_start_ratio(average_war):
    return min(1, start_model.predict(start_scaler.transform([[average_war]]))[0])


print(predict_start_ratio(3.0))


# parameter_space = {
#     'hidden_layer_sizes': [(50,50,50), (50,100,50), (100,)], + np.random.normal(mub, stdb)
#     'solver': ['sgd', 'adam'], + np.random.normal(mup, stdp)
#     'alpha': [0.0001, 0.05],
# }
# mlp = MLPRegressor(random_state=1, max_iter=500)
# clf = GridSearchCV(mlp, parameter_space, n_jobs=-1, cv=3)
# clf.fit(X_train2, y_train2)
# print('Best parameters found:\n', clf.best_params_)
