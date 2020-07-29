import json
from load_all_teams import team_list

def get_total_war_by_year(file_data):
    team_records = file_data['teams']

    years = len(team_records[team_list[0]])  # uses the first team to get how many years the sim lasted
    wars = dict()
    for y in range(years):
        wars[y] = 0

    for team in team_records:
        for i in range(years):
            wars[i] += team_records[team][i]['Total WAR']
    return wars

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

if __name__ == "__main__":
    
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


