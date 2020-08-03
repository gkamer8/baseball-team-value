import json
from load_all_teams import team_list

def get_total_stat_by_year(file_data, key):
    team_records = file_data['teams']

    years = len(team_records[team_list[0]])  # uses the first team to get how many years the sim lasted
    wars = dict()
    for y in range(years):
        wars[y] = 0

    for team in team_records:
        for i in range(years):
            wars[i] += team_records[team][i][key]
    return wars

def get_total_war_by_year(file_data):
    return get_total_stat_by_year(file_data, 'Total WAR')

# Looks at EXPECTED wl, not actual wl
def get_avg_wl_by_year(file_data):
    wars = get_total_war_by_year(file_data)
    wls = dict()
    for year in wars:
        wls[year] = ((.294 * 162) + (wars[year] / 30)) / 162
    return wls

def get_war_by_source_by_year(file_data):
    team_records = file_data['teams']

    years = len(team_records[team_list[0]])  # uses the first team to get how many years the sim lasted
    wars = dict()
    for y in range(years):
        wars[y] = {'FA': 0, 'Contracts': 0, 'Prospects': 0}
    
    for team in team_records:
        for i in range(years):
            wars[i]['FA'] += team_records[team][i]['FA WAR']
            wars[i]['Prospects'] += team_records[team][i]['Sim Prospect WAR']
            wars[i]['Contracts'] += team_records[team][i]['Total WAR'] - (team_records[team][i]['Sim Prospect WAR'] + team_records[team][i]['FA WAR'])
        
    return wars

def get_war_by_source_percentage_by_year(file_data):
    wars = get_war_by_source_by_year(file_data)

    wars2 = dict()
    for year in wars:
        wars2[year] = dict()
        total = wars[year]['FA'] + wars[year]['Prospects'] + wars[year]['Contracts']
        wars2[year]['FA'] = wars[year]['FA'] / total
        wars2[year]['Prospects'] = wars[year]['Prospects'] / total
        wars2[year]['Contracts'] = wars[year]['Contracts'] / total
    return wars2

def average_many_wls(file_datas):
    new = dict()
    num_files = len(file_datas)
    for f in file_datas:
        wls = get_avg_wl_by_year(f)
        for year in wls:
            if year in new:
                new[year] += wls[year]
            else:
                new[year] = wls[year]
    for k in new:
        new[k] = new[k] / num_files
    
    return new

def get_avg_stat_by_year(file_data, key):
    stats = get_total_stat_by_year(file_data, key)
    for year in stats:
        stats[year] = stats[year] / 30
    return stats

# Average *average* championship probability across multiple files and teams
def get_avg_championships_by_year(file_data):
    return get_avg_stat_by_year(file_data, 'Championship Probability')

# Average combined championship probability across multiple files
def average_many_total_championships(file_datas):
    new = dict()
    num_files = len(file_datas)
    for f in file_datas:
        champs = get_total_stat_by_year(f, 'Championship Probability')
        for year in champs:
            if year in new:
                new[year] += champs[year]
            else:
                new[year] = champs[year]
    for k in new:
        new[k] = new[k] / num_files
    
    return new

# Looks at multiple sims and gets an average of championship probability for each team
def get_final_numbers(file_datas, discount_rate):
    new = dict()
    num_files = len(file_datas)
    for f in file_datas:
        for team in f['teams']:
            stat = 0
            years = f['teams'][team]
            for year in range(len(years)):
                stat += years[year]['Championship Probability'] / (1 + discount_rate) ** year
            if team not in new:
                new[team] = stat
            else:
                new[team] = new[team] + stat
    for team in new:
        new[team] = new[team] / num_files
    return new

if __name__ == "__main__":
    
    """
    filename = "Sim Records/v1.json"
    sim = json.load(open(filename))

    print("League WL by Year:")
    wars = get_avg_wl_by_year(sim)
    for year in wars:
        print(f"{year + 2020}: {wars[year]:0.3f}")
    
    print("\nLeague WAR Sources by Year")
    war_sources = get_war_by_source_percentage_by_year(sim)
    for year in wars:
        print(f"{year + 2020}: FA: {war_sources[year]['FA']:0.3f}, Prospects: {war_sources[year]['Prospects']:0.3f}, Contracts: {war_sources[year]['Contracts']:0.3f}")

    print("\nAverage WL:")
    all_wls = average_many_wls([json.load(open(f"Sim Records/run{x}.json")) for x in range(10)])
    for year in all_wls:
        print(f"{year + 2020}: {all_wls[year]:0.3f}")

    print("\nAverage Total Champs:")
    champs = average_many_total_championships([json.load(open(f"Sim Records/run{x}.json")) for x in range(10)])
    for year in champs:
        print(f"{year + 2020}: {champs[year]:0.3f}")
    """

    fs = [json.load(open(f"Sim Records/run{x}.json")) for x in range(10)]
    probs = get_final_numbers(fs, .25)
    probs = {k: v for k, v in sorted(probs.items(), key=lambda item: item[1], reverse=True)}
    fhand = open('results.csv', 'w')
    fhand.write("Team,Value\n")
    for team in probs:
        fhand.write(f"{team.capitalize()},{probs[team]:0.3}\n")
    fhand.close()
    
    


