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

if __name__ == "__main__":
    
    filename = "Sim Records/v1.json"
    sim = json.load(open(filename))

    wars = get_avg_wl_by_year(sim)
    for year in wars:
        print(f"{year + 2020}: {wars[year]:0.3f}")


