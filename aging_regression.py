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
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.datasets import make_regression
from sklearn.preprocessing import StandardScaler, Normalizer


# Takes an age integer and returns the appropriate key in the model-data dictionaries
def age_bucket_mapper(age):
    if 24 <= age < 35:
        return str(float(age))
    else:
        if age < 22:
            return "22-"
        elif 22 <= age < 24:
            return "22-24"
        elif 35 <= age <= 38:
            return "35-38"
        elif age > 38:
            return "38+"


# Takes an war float and returns the appropriate key in the model-data dictionaries
def war_bucket_mapper(war):
    if war < 0:
        return "neg"
    elif 0 <= war <= 1:
        return "0-1"
    elif 1 < war <= 2:
        return "1-2"
    elif 2 < war <= 4:
        return "2-4"
    elif 4 < war <= 7:
        return "4-7"
    elif war > 7:
        return "7+"


# Loading career war data into dataframes
batting_df = pd.read_csv('Aging Data/Batters_WAR_by_Age.csv')
pitching_df = pd.read_csv('Aging Data/Pitchers_WAR_by_Age.csv')

def filter_data(df):
    df_list = []
    for i in range(2, len(df) - 1):
        age_2 = float(df.loc[i - 2, "Age"])
        age0 = float(df.loc[i - 1, "Age"])
        age1 = float(df.loc[i, "Age"])
        age2 = float(df.loc[i + 1, "Age"])
        war0 = float(df.loc[i - 1, "WAR"])
        war1 = float(df.loc[i, "WAR"])
        war2 = float(df.loc[i + 1, "WAR"])
        war_2 = float(df.loc[i - 2, "WAR"])
        if age1 == age2 - 1 and -12 < war2 - war1 < 12 and age0 == age1 - 1 and age_2 == age0 - 1:
            df_list.append({"WAR": war2, "Age": age2, "Previous War": war1, "2yr War": war0, "3yr War": war_2})
    df = pd.DataFrame(df_list)
    df.to_csv('regression_data1.csv')
    return df


batting = filter_data(batting_df)
batting1 = batting
y = batting["WAR"]

# plt.hist(batting["Previous War"], bins=100, density=True, alpha=0.6, color='g')
# plt.show()
# ages = pd.get_dummies(batting["Age"], drop_first=True)
# batting = batting.drop('Age', axis=1)
# batting = batting.drop('WAR', axis=1)
# X = pd.concat([ages, batting], axis=1)
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=9)
# lin_reg_mod = LinearRegression()
# lin_reg_mod.fit(X_train, y_train)
# pred = lin_reg_mod.predict(X_test)
# test_set_rmse = (np.sqrt(mean_squared_error(y_test, pred)))
# test_set_r2 = r2_score(y_test, pred)
# #
# print(test_set_rmse)
# print(test_set_r2)
# print(X.columns)
# print(lin_reg_mod.coef_)
# print(lin_reg_mod.intercept_)
# std = (mean_squared_error(y_test, pred))**0.5
# effects = {}
# for i in range(len(X.columns)):
#     effects[X.columns[i]] = lin_reg_mod.coef_[i]
# effects['22-'] = 0
# print(effects)
# print(lin_reg_mod.intercept_)
# effects1 = {'22-24': -0.8356828669818591, '24.0': -1.2088822514203854, '25.0': -1.3318586036639184, '26.0': -1.5562226521131843, '27.0': -1.8313645466742081, '28.0': -1.9208418921615453, '29.0': -1.9982135910865508, '30.0': -2.10345382229555, '31.0': -2.0837876583887334, '32.0': -2.278657027155815, '33.0': -2.4264427241857356, '34.0': -2.4182867848208858, '35-38': -2.4491587863725828, '38+': -2.6392730179268122, 'Previous War': 0.38541517063057995, '2yr War': 0.23297168544979685, '3yr War': 0.1434267856022, '22-': 0}
# effects = {'22-24': -0.8356828669818117, '24.0': -1.2088822514203437, '25.0': -1.3318586036638898, '26.0': -1.556222652113156, '27.0': -1.8313645466741741, '28.0': -1.9208418921615207, '29.0': -1.9982135910865215, '30.0': -2.1034538222955206, '31.0': -2.083787658388702, '32.0': -2.278657027155786, '33.0': -2.4264427241857054, '34.0': -2.418286784820855, '35-38': -2.4491587863725535, '38+': -2.6392730179267834, 'Previous War': -0.6145848293694183, '2yr War': 0.23297168544979696, '3yr War': 0.14342678560220112, '22-': 0}
# intercept = 2.2133141059317847


# def mean(age, war1, war2, war_2):
#     return intercept + effects[age] + effects['Previous War']*war1 + effects['2yr War']*war2 + effects['3yr War']*war_2




# def fn(x, a, b, c, d):
#     return a + b*(x[0]) + c*(x[1]) + d*(x[2])
#
#
# x = np.array([batting["Previous War"].to_list(),batting["Age"].to_list(), batting["2yr War"].to_list()])
# y = np.array(batting["WAR Delta"].to_list())
#
# popt, pcov = curve_fit(fn, x, y)
#
# print(popt)
# plt.scatter(batting1["Age2"], batting1["Previous War"])
# # plt.title('Scatter plot pythonspot.com')
# plt.xlabel('x')
# plt.ylabel('y')
# plt.show()


std = batting.std(axis=0, skipna=True)
mean = batting.mean(axis=0, skipna=True)
print(mean)
X = batting.drop('WAR', axis=1)
print(X.columns)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=1)
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.fit_transform(X_test)
regr = MLPRegressor(random_state=1, max_iter=500).fit(X_train, y_train)
print(X_test[:4])
print(regr.predict(X_test[:4]))

def war_predictor(age, war1, war2, war3):
    return regr.predict(pd.DataFrame({'Age2': (age - mean['Age'])/std['Age'], 'Previous War': (war1 - mean['Previous War'])/std['Previous War'], '2yr War': (war2 - mean['2yr War'])/std['2yr War'], '3yr War': (war3 - mean['3yr War'])/std['3yr War']}, index=[0]))
print(war_predictor(29.0, 8.6, 9.8, 6.8))
print(regr.score(X_test, y_test))

# plt.scatter(regr.predict(X_train), regr.predict(X_train) - y_train)
# plt.ylabel('Residuals')
# plt.title('Residual Plot For War Prediction Model')
# plt.show()

# max1 = batting.max(axis=0, skipna=True)
# min1 = batting.min(axis=0, skipna=True)
# print(max1)
# print(min1)
# X = batting.drop('WAR', axis=1)
# print(X.columns)
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=1)
# sc = Normalizer()
# X_train = sc.fit_transform(X_train)
# X_test = sc.fit_transform(X_test)
# regr = MLPRegressor(random_state=1, max_iter=500).fit(X_train, y_train)
# print(X_test[:4])
# print(regr.predict(X_test[:4]))
#
# def war_predictor(age, war1, war2, war3):
#     return regr.predict(pd.DataFrame({'Age': (age - min1['Age'])/(max1['Age']- min1['Age']), 'Previous War': (war1 - min1['Previous War'])/(max1['Previous War']- min1['Previous War']), '2yr War': (war2 - min1['2yr War'])/(max1['2yr War']- min1['2yr War']), '3yr War': (war3 - min1['3yr War'])/(max1['3yr War'] - min1['3yr War'])}, index=[0]))
# print(war_predictor(22.0, 3.0, 4.0, 1.2))
# print(regr.score(X_test, y_test))


# y1 = batting["WAR"]
# ages = pd.get_dummies(batting["Age"], drop_first=True)
# batting = batting.drop('Age', axis=1).drop('Age2', axis=1)
# batting = batting.drop('WAR', axis=1)
# X1 = pd.concat([ages, batting], axis=1)
# X_train1, X_test1, y_train1, y_test1 = train_test_split(X1, y1, test_size = 0.2, random_state=1)
# regr1 = MLPRegressor(random_state=1, max_iter=500).fit(X_train1, y_train1)
# print(X_test1[:4])
# print(regr1.predict(X_test1[:4]))
# print(regr1.score(X_test1, y_test1))



