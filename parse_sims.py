import json
from load_all_teams import team_list


def print_first_year_payrolls(fname):
    team_records = json.load(open(fname))['teams']
    teams = {k: v for k, v in sorted(team_records.items(), key=lambda item: item[1][0]['Max Payroll'], reverse=True)}

    print('\nPayrolls:')
    for team in teams:
        print(f"{team.capitalize()}: ${teams[team][0]['Max Payroll']:,.2f}")


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
            wars[i]['Contracts'] += team_records[team][i]['Total WAR'] - (team_records[team][i]['Sim Prospect WAR'] +
                                                                          team_records[team][i]['FA WAR'])
        
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


# Gets championship probabilities for each year for each team
def get_championships_per_team_per_year(file_datas):
    new = dict()
    num_files = len(file_datas)
    for f in file_datas:
        for team in f['teams']:
            prob_by_year = [f['teams'][team][i]['Championship Probability'] for i in range(len(f['teams'][team]))]
            if team not in new:
                new[team] = prob_by_year
            else:
                new[team] = [prob_by_year[i] + new[team][i] for i in range(len(new[team]))]
    for team in new:
        new[team] = [new[team][i] / num_files for i in range(len(new[team]))]
    return new


def export_championships_per_team_per_year(fnames, outfile='champs.csv'):
    file_datas = [json.load(open(fname)) for fname in fnames]
    teams = get_championships_per_team_per_year(file_datas)
    
    # Sort by first year championship value
    teams = {k: v for k, v in sorted(teams.items(), key=lambda item: item[1][0], reverse=True)}

    fhand = open(outfile, 'w')
    num_years = len(teams[list(teams.keys())[0]])
    header = 'Team,'
    for i in range(num_years):
        header += f'Year {i + 1},'
    header = header[:-1] + '\n'
    fhand.write(header)
    for team in teams:
        to_add = f"{team.capitalize()},"
        for i in range(num_years):
            to_add += str(f"{teams[team][i]:0.3}") + ','
        to_add = to_add[:-1] + '\n'
        fhand.write(to_add)
    fhand.close()


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


# Exports csv with final team value numbers
def export_team_values(fnames, outfile='results.csv', discount=0.25):

    fs = [json.load(open(fname)) for fname in fnames]
    probs = get_final_numbers(fs, discount)
    probs = {k: v for k, v in sorted(probs.items(), key=lambda item: item[1], reverse=True)}
    fhand = open(outfile, 'w')
    fhand.write("Team,Value\n")
    for team in probs:
        fhand.write(f"{team.capitalize()},{probs[team]:0.3}\n")
    fhand.close()


def print_average_championships(fnames):
    print("\nAverage Total Champs:")
    champs = average_many_total_championships([json.load(open(fname)) for fname in fnames])
    for year in champs:
        print(f"{year + 2020}: {champs[year]:0.3f}")


def print_average_wl(fnames):
    print("\nAverage WL:")
    all_wls = average_many_wls([json.load(open(fname)) for fname in fnames])
    for year in all_wls:
        print(f"{year + 2020}: {all_wls[year]:0.3f}")


def average_many_sources(file_datas):
    sources = dict()
    num_files = len(file_datas)
    for data in file_datas:
        war_sources = get_war_by_source_percentage_by_year(data)
        for key in war_sources:
            if key in sources:
                sources[key]['FA'] += war_sources[key]['FA']
                sources[key]['Prospects'] += war_sources[key]['Prospects']
                sources[key]['Contracts'] += war_sources[key]['Contracts']
            else:
                sources[key] = dict(
                            {
                                'FA': war_sources[key]['FA'],
                                'Prospects':  war_sources[key]['Prospects'],
                                'Contracts': war_sources[key]['Contracts']
                            })

    for key in sources:
        sources[key]['FA'] = sources[key]['FA'] / num_files
        sources[key]['Prospects'] = sources[key]['Prospects'] / num_files
        sources[key]['Contracts'] = sources[key]['Contracts'] / num_files
    return sources


def print_average_sources(fnames):
    print("\nAverage Sources:")
    war_sources = average_many_sources([json.load(open(fname)) for fname in fnames])
    for year in war_sources:
        print(f"{year + 2020}: FA: {war_sources[year]['FA']:0.3f}, Prospects: {war_sources[year]['Prospects']:0.3f}, Contracts: {war_sources[year]['Contracts']:0.3f}")
