import pandas as pd
from scipy.stats import norm


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
batting_df = pd.read_csv('Aging Data\\Batters_WAR_by_Age.csv')
pitching_df = pd.read_csv('Aging Data\\Pitchers_WAR_by_Age.csv')

# Initializing dictionaries to hold model parameters
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


# Calculates change in WAR by age and war category, and stores the data in dictionary
def find_deltas_by_age(df, batting):
    if batting:
        tmp_progressions = progression_data_b
    else:
        tmp_progressions = progression_data_p
    for i in range(len(df) - 1):
        age1 = float(df.loc[i, "Age"])
        age2 = float(df.loc[i+1, "Age"])
        war1 = float(df.loc[i, "WAR"])
        war2 = float(df.loc[i+1, "WAR"])
        if age1 == age2 - 1 and -12 < war2 - war1 < 12:
            age_bucket = age_bucket_mapper(age2)
            war_bucket = war_bucket_mapper(war1)
            tmp_progressions[age_bucket][war_bucket].append(war2 - war1)

    return tmp_progressions


# Fits change in war data to a normal distribution for each age/war category stores parameters
def get_model_parameters(deltas):
    parameters_by_year = {}
    for key1 in deltas.keys():
        parameters_by_year[key1] = {}
        for key2 in deltas[key1].keys():
            if len(deltas[key1][key2]) > 1:
                mu, std = norm.fit(deltas[key1][key2])
                parameters_by_year[key1][key2] = (mu, std)
            else:
                parameters_by_year[key1][key2] = 0, 1
    return parameters_by_year


# Runs the functions above and returns the dictionaries containing model parameters
def getmodels():
    batting_deltas = find_deltas_by_age(batting_df, True)
    batting_models = get_model_parameters(batting_deltas)

    pitching_deltas = find_deltas_by_age(pitching_df, False)
    pitching_models = get_model_parameters(pitching_deltas)
    return batting_models, pitching_models

