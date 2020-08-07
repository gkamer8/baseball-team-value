import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR
import random
import math
import matplotlib.pyplot as plt
import scipy
import pickle

"""

This script takes the data obtained via war_data_scraping.py and fits it to an
appropriate model. The function war_predictor is used to progress players in
the simulation based on the fitted model's prediction and a normally distributed
error term.

"""

# File locations for saved models
b_prospect_adjust = 'Player Models/batter_prospect_war_adjustment_model.sav'
p_prospect_adjust = 'Player Models/pitcher_prospect_war_adjustment_model.sav'

b_model = 'Player Models/batter_progression_model.sav'
p_model = 'Player Models/pitcher_progression_model.sav'
b_sc = 'Player Models/batter_data_scaler.sav'
p_sc = 'Player Models/pitcher_data_scaler.sav'
b_resid = 'Player Models/batter_model_residuals.sav'
p_resid = 'Player Models/pitcher_model_residuals.sav'

st_model = 'Player Models/pitcher_start_model.sav'
st_scaler = 'Player Models/pitcher_start_data_scaler.sav'


def average(list1):
    return sum(list1[-4:]) / len(list1[-4:])


def new_floor(num):
    if num > 0:
        return math.floor(num)
    else:
        return math.ceil(num)


def get_residual_dict(df1):
    df1['residuals'] = df1['residuals'].apply(new_floor)
    dict1 = {}
    df0 = df1[df1['war'] < 0]
    df01 = df1[df1['war'] < 1]
    df01 = df01[df01['war'] >= 0]
    df12 = df1[1 <= df1['war']]
    df12 = df12[df12['war'] < 2]
    df23 = df1[2 <= df1['war']]
    df23 = df23[df23['war'] < 3]
    df34 = df1[3 <= df1['war']]
    df34 = df34[df34['war'] < 4]
    df45 = df1[4 <= df1['war']]
    df45 = df45[df45['war'] < 5]
    df6 = df1[df1['war'] >= 5]
    dict1['0'] = df0['residuals'].to_list()
    dict1['01'] = df01['residuals'].to_list()
    dict1['12'] = df12['residuals'].to_list()
    dict1['23'] = df23['residuals'].to_list()
    dict1['34'] = df34['residuals'].to_list()
    dict1['45'] = df45['residuals'].to_list()
    dict1['6'] = df6['residuals'].to_list()
    return dict1


def war_mapper(war):
    if war < 0:
        return '0'
    elif 0 <= war < 1:
        return '01'
    elif 1 <= war < 2:
        return '12'
    elif 2 <= war < 3:
        return '23'
    elif 3 <= war < 4:
        return '34'
    elif 4 <= war < 5:
        return '45'
    else:
        return '6'


def filter_data(df, pitcher):
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
    return dct


def pitcher_start_data(df):
    df_list = []
    indexes = list(df.index)
    for i in indexes:
        if df.loc[i, 'pitcher']:
            wars = df.loc[i, 'WAR']
            start_ratio = df.loc[i, 'start_ratio']
            df_list.append({"Average WAR": sum(wars[:6]) / len(wars[:6]), "ratio": start_ratio})
    return pd.DataFrame(df_list)


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
    residuals = list(y - neigh.predict(X))
    wars = list(neigh.predict(X))
    resid_df = pd.DataFrame(list(zip(residuals, wars)),
                            columns=['residuals', 'war'])
    return neigh, sc, resid_df


def getNeural(df):
    regr = MLPRegressor(max_iter=500, hidden_layer_sizes=(50,100,50), alpha=0.05, learning_rate='constant')
    y = df["WAR"]
    X = df.drop("WAR", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    X = sc.transform(X)
    regr.fit(X_train, y_train)
    print(regr.score(X_test, y_test))
    residuals = list(y - regr.predict(X))
    wars = list(regr.predict(X))
    resid_df = pd.DataFrame(list(zip(residuals, wars)),
               columns =['residuals', 'war'])
    return regr, sc, resid_df


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
    residuals = list(y - regr.predict(X))
    wars = list(regr.predict(X))
    resid_df = pd.DataFrame(list(zip(residuals, wars)),
                            columns=['residuals', 'war'])
    return regr, sc, resid_df


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
    residuals = list(y - regr.predict(X))
    wars = list(regr.predict(X))
    resid_df = pd.DataFrame(list(zip(residuals, wars)),
                            columns=['residuals', 'war'])
    return regr, sc, resid_df


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
    residuals = list(y - regr.predict(X))
    wars = list(regr.predict(X))
    resid_df = pd.DataFrame(list(zip(residuals, wars)),
                            columns=['residuals', 'war'])
    return regr, sc, resid_df


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
    residuals = list(y - regr.predict(X))
    wars = list(regr.predict(X))
    resid_df = pd.DataFrame(list(zip(residuals, wars)),
                            columns=['residuals', 'war'])
    return regr, sc, resid_df


# Decides which model type the player progression is built on
def getModel(df):
    return getNeural(df)


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
    return regr, sc


if __name__ == "__main__":
    df = pd.read_csv('Aging Data/historical_WAR_by_age_data.csv', converters={'WAR': eval, 'Age': eval, "Games": eval})
    df = df[df['Age'] != "--"]
    batting_df = df[df['pitcher'] == False].drop("pitcher", axis=1)
    pitching_df = df[df['pitcher'] == True].drop("pitcher", axis=1)

    batting = filter_data(df, False)
    pitching = filter_data(df, True)
    bat_model, scb, resid_dfb = getModel(batting)
    pitch_model, scp, resid_dfp = getModel(pitching)
    residualsb = get_residual_dict(resid_dfb)
    residualsp = get_residual_dict(resid_dfp)

    pickle.dump(bat_model, open(b_model, 'wb'))
    pickle.dump(pitch_model, open(p_model, 'wb'))
    pickle.dump(scb, open(b_sc, 'wb'))
    pickle.dump(scp, open(p_sc, 'wb'))
    pickle.dump(residualsb, open(b_resid, 'wb'))
    pickle.dump(residualsp, open(p_resid, 'wb'))

    b_prospect_data = prospect_conversion_data(df, False)
    p_prospect_data = prospect_conversion_data(df, True)

    pickle.dump(b_prospect_data, open(b_prospect_adjust, 'wb'))
    pickle.dump(p_prospect_data, open(p_prospect_adjust, 'wb'))

    pitcher_starts = pitcher_start_data(df)

    start_model, start_scaler = getModelforStarts(pitcher_starts)

    pickle.dump(start_model, open(st_model, 'wb'))
    pickle.dump(start_scaler, open(st_scaler, 'wb'))

bat_model = pickle.load(open(b_model, 'rb'))
pitch_model = pickle.load(open(p_model, 'rb'))
scb = pickle.load(open(b_sc, 'rb'))
scp = pickle.load(open(p_sc, 'rb'))
residualsb = pickle.load(open(b_resid, 'rb'))
residualsp = pickle.load(open(p_resid, 'rb'))

adjust_batters = pickle.load(open(b_prospect_adjust, 'rb'))
adjust_pitchers = pickle.load(open(p_prospect_adjust, 'rb'))

start_model = pickle.load(open(st_model, 'rb'))
start_scaler = pickle.load(open(st_scaler, 'rb'))


def war_predictor(age, war, average, pitching, start_ratio):
    if pitching:
        return pitch_model.predict(scp.transform([[age, war, average, start_ratio]]))[0]
    else:
        return bat_model.predict(scb.transform([[age, war, average]]))[0]


def error_predictor(pitcher, war):
    num = random.uniform(0, 1)
    if num > -1:
        war = war_mapper(war)
        if pitcher:
            return random.choice(residualsp[war])
        else:
            return random.choice(residualsb[war])
    else:
        return 0


def adjust_prospect_war(war, age, pitcher):
    if pitcher:
        return war - adjust_batters[age]
    else:
        return war - adjust_pitchers[age]


def predict_start_ratio(average_war):
    return min(1, start_model.predict(start_scaler.transform([[average_war]]))[0])


