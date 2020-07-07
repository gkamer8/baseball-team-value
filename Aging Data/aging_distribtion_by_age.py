import pandas as pd
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt


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

batting_df = pd.read_csv('Batters_WAR_by_Age.csv')
pitching_df = pd.read_csv('Pitchers_WAR_by_Age.csv')
progression_data_b = {}
progression_data_p = {}
age_buckets = ["22-", "22-24", "35-38", "38+"]
war_buckets = ["neg", "0-1", "1-2", "2-4", "4-7", "7+"]

for bucket1 in age_buckets:
    progression_data_b[bucket1] = {}
    progression_data_p[bucket1] = {}
    for bucket2 in war_buckets:
        progression_data_b[bucket1][bucket2] = []
        progression_data_p[bucket1][bucket2] = []

for i in range(24, 35):
    progression_data_b[str(float(i))] = {}
    progression_data_p[str(float(i))] = {}
    for bucket2 in war_buckets:
        progression_data_b[str(float(i))][bucket2] = []
        progression_data_p[str(float(i))][bucket2] = []
print(progression_data_b)

def find_deltas_by_age(df, batting):
    if batting:
        tmp_progressions = progression_data_b
    else:
        tmp_progressions = progression_data_p
    for i in range(len(df) - 1):
        print(i)
        age1 = float(df.loc[i, "Age"])
        age2 = float(df.loc[i+1, "Age"])
        war1 = float(df.loc[i, "WAR"])
        war2 = float(df.loc[i+1, "WAR"])
        if age1 == age2 - 1 and -12 < war2 - war1 < 12:
            age_bucket = age_bucket_mapper(age2)
            war_bucket = war_bucket_mapper(war1)
            tmp_progressions[age_bucket][war_bucket].append(war2 - war1)

    return tmp_progressions


def get_model_parameters(deltas):
    parameters_by_year = {}
    for key1 in deltas.keys():
        parameters_by_year[key1] = {}
        for key2 in deltas[key1].keys():
            if len(deltas[key1][key2]) > 1:
                mu, std = norm.fit(deltas[key1][key2])
                parameters_by_year[key1][key2] = (mu, std)
                print(len(deltas[key1][key2]))
                print("Age: " + key1)
                print("war group: " + key2)
                print("mean: " + str(mu))
                print("std: " + str(std))
            else:
                parameters_by_year[key1][key2] = 0, 1
    return parameters_by_year


def get_models():
    batting_deltas = find_deltas_by_age(batting_df, True)
    batting_models = get_model_parameters(batting_deltas)

    pitching_deltas = find_deltas_by_age(pitching_df, False)
    pitching_models = get_model_parameters(pitching_deltas)
    print(pitching_models)
    print(batting_models)
    return batting_models, pitching_models


get_models()
# mu, std = norm.fit(progression_data["30"])
#
# # Plot the histogram.
# plt.hist(progression_data["30"], bins=25, density=True, alpha=0.6, color='g')
#
# # Plot the PDF.
# xmin, xmax = plt.xlim()
# x = np.linspace(xmin, xmax, 100)
# p = norm.pdf(x, mu, std)
# plt.plot(x, p, 'k', linewidth=2)
# title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
# plt.title(title)
#
# plt.show()
#
# print(progression_data)
