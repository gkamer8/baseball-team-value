import csv

# List of team abbreviations (baseball reference compatible)
team_names = [
    "NYY",
    "BAL",
    "TBR",
    "BOS",
    "TOR",
    "TBD",

    "KCR",
    "CLE",
    "MIN",
    "DET",
    "CHW",

    "OAK",
    "TEX",
    "HOU",
    "SEA",
    "LAA",
    "ANA",

    "NYM",
    "MIA",
    "WSN",
    "ATL",
    "PHI",
    "FLA",
    "MON",

    "CHC",
    "STL",
    "PIT",
    "CIN",
    "MIL",
    "LAD",
    "SDP",
    "SFG",
    "ARI",
    "COL"
]

# Dictionary of team abbreviations to division (numbered)
divisions_dict = {
    "NYY": 0,
    "BAL": 0,
    "TBR": 0,
    "BOS": 0,
    "TOR": 0,
    "TBD": 0,

    "KCR": 1,
    "CLE": 1,
    "MIN": 1,
    "DET": 1,
    "CHW": 1,

    "OAK": 2,
    "TEX": 2,
    "HOU": 2,
    "SEA": 2,
    "LAA": 2,
    "ANA": 2,

    "NYM": 3,
    "MIA": 3,
    "WSN": 3,
    "ATL": 3,
    "PHI": 3,
    "FLA": 3,
    "MON": 3,

    "CHC": 4,
    "STL": 4,
    "PIT": 4,
    "CIN": 4,
    "MIL": 4,

    "LAD": 5,
    "SDP": 5,
    "SFG": 5,
    "ARI": 5,
    "COL": 5
}

# returns master list, which is list of teams since 2000 with attributes: name, year, league, wl, and war
def load_data():
    master = []

    # go through batting first and add teams

    filenames = ['00-04.csv', '05-09.csv', '10-14.csv', '15-19.csv']

    for f in filenames:

        with open('batting/' + f) as csvfile:
            this_file = []
            reader = csv.reader(csvfile)
            next(reader)  # skips header line
            for r in reader:
                name = r[2]
                year = int(r[1])
                league = r[3]
                wl = float(r[6])  # win-loss percentage
                war = float(r[18])

                mydict = {'name': name, 'year': year, 'league': league, 'wl': wl, 'war': war}
                this_file.append(mydict)

            master.extend(this_file)

    # add pitching war

    for f in filenames:

        with open('pitching/' + f) as csvfile:
            this_file = []
            reader = csv.reader(csvfile)
            next(reader)  # skips header line
            for r in reader:
                war = float(r[21])
                name = r[2]
                year = int(r[1])

                #  go to team in master and add pitching WAR
                not_found = True
                for t in master:
                    if t['name'] == name and t['year'] == year:
                        t['war'] += war
                        not_found = False
                        break
                if not_found:
                    print("Not found")

    return master

# From a line of team data with name and year, return boolean of whether team won division
def won_division(team_data):
    data = load_data()

    if team_data['wl'] >= .66:
        return True
    elif team_data['wl'] <= .44:
        return False

    div = divisions_dict[team_data['name']]
    other_records = []
    for dat in data:
        if dat['year'] == team_data['year'] and divisions_dict[dat['name']] == div:
            other_records.append(dat['wl'])

    return max(other_records) <= team_data['wl']

# From a line of team data with name and year, return boolean of whether team made the playoffs
def made_playoffs(team_data):
    data = load_data()
    
    if won_division(team_data):
        return True
    other_records = []
    for dat in data:
        if dat['year'] == team_data['year'] and team_data['league'] == dat['league']:
            if won_division(dat):
                continue
            other_records.append(dat['wl'])

    second_best = 0
    for o in other_records:
        if o != max(other_records) and o > second_best:
            second_best = o
    return team_data['wl'] >= second_best
