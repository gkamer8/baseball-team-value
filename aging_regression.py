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
        age0 = float(df.loc[i - 1, "Age"])
        age1 = float(df.loc[i, "Age"])
        age2 = float(df.loc[i + 1, "Age"])
        war0 = float(df.loc[i - 1, "WAR"])
        war1 = float(df.loc[i, "WAR"])
        war2 = float(df.loc[i + 1, "WAR"])
        if age1 == age2 - 1 and -12 < war2 - war1 < 12 and age0 == age1 - 1:
            df_list.append({"WAR Delta": war2 - war1, "Age": age_bucket_mapper(age2), "Previous War": war1, "2yr War": war0})
    df = pd.DataFrame(df_list)
    df.to_csv('regression_data1.csv')
    return df


batting = filter_data(batting_df)
y = batting["WAR Delta"]

ages = pd.get_dummies(batting["Age"], drop_first=True)
batting = batting.drop('Age', axis=1)
batting = batting.drop('WAR Delta', axis=1)
X = pd.concat([ages, batting], axis=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=9)
lin_reg_mod = LinearRegression()
lin_reg_mod.fit(X_train, y_train)
pred = lin_reg_mod.predict(X_test)
test_set_rmse = (np.sqrt(mean_squared_error(y_test, pred)))
test_set_r2 = r2_score(y_test, pred)
#
# print(test_set_rmse)
# print(test_set_r2)
# print(lin_reg_mod.coef_)
# print(lin_reg_mod.intercept_)
std = (mean_squared_error(y_test, pred))**0.5
effects = {}
for i in range(len(X.columns)):
    effects[X.columns[i]] = lin_reg_mod.coef_[i]
def mean(age, war1, war2):
    return lin_reg_mod.intercept + effects[age] + effects['Previous War']*war1 + effects['2yr War']*war2



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
# plt.scatter(batting["Age"], batting["WAR Delta"])
# plt.title('Scatter plot pythonspot.com')
# plt.xlabel('x')
# plt.ylabel('y')
# plt.show()




