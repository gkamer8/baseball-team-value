import pandas as pd
from selenium import webdriver
import selenium
import re
from math import isnan

"""

This script scrapes data from baseballreference on career war by year,
career games played by year, position, and percent of games started
as pitcher for each player under contract

"""

driver = webdriver.Chrome("C:\\Users\\jsimp\\Downloads\\chromedriver_win32\\chromedriver.exe")


# def get_service_time(lst):
#     for item in lst:
#         if "Service Time" in item:
#             return re.findall("[0-9]+\.[0-9]+", item)[0]


def format_correctly(lst):
    return [{'type': typ, 'value': sal} for (yr, sal, typ) in lst]


def delete_dups(lst):
    years = []
    new_lst = []
    for (yr, sal, nt) in lst:
        if yr not in years:
            new_lst.append((yr, sal, nt))
            years.append(yr)
    return new_lst


def change_contract_names(notes):
    new_lst = []
    for item in notes:
        if "Team Option" in item:
            new_lst.append('team option')
        elif "Mutual Option" in item:
            new_lst.append('mutual option')
        elif "Player Option" in item:
            new_lst.append('player option')
        elif "Vesting Option" in item:
            new_lst.append('vesting option')
        else:
            new_lst.append('salary')
    return new_lst


def append_contracts(lst, srv):
    srv += len(lst)
    while srv < 3:
        lst.append((None, None, 'pre-arb'))
        srv += 1
    while srv < 6:
        lst.append((None, None, 'arb'))
        srv += 1
    return lst


def merge_lsts(yrs, sals, nts):
    lst = zip(yrs, sals, nts)
    return [(yr, sal, nt) for (yr, sal, nt) in lst if yr >= 2020]


def extract_salary(list):
    list_new = []
    for item in list:
        tmp = item.text
        tmp = tmp.replace("$", "").replace(",", "").replace("*", "")
        try:
            list_new.append(float(tmp))
        except ValueError:
            list_new.append("")
    return list_new


def extract_type(list):
    return [item.text for item in list]


def extract_year(list):
    list_new = []
    for item in list:
        tmp = item.text
        try:
            list_new.append(int(tmp))
        except ValueError:
            list_new.append(0)

    return list_new


def data_scraper(name):
    print(name)
    link = "https://www.baseball-reference.com/players/" + name[0] + "/" + name + ".shtml"
    driver.get(link)
    yrs = []
    salaries = []
    notes = []
    try:
        tmp = driver.find_element_by_id('br-salaries').find_element_by_tag_name('tbody')
        yrs = extract_year(tmp.find_elements_by_css_selector('[data-stat="year_ID"]'))
        salaries = extract_salary(tmp.find_elements_by_css_selector('[data-stat="Salary"]'))
        notes = extract_type(tmp.find_elements_by_css_selector('[data-stat="notes"]'))
    except selenium.common.exceptions.NoSuchElementException:
        print(name + "arbitration only")
    return yrs, salaries, notes


def construct_contracts(team):
    contract_lst = []
    df = pd.read_csv('Full Team Data/' + team + '_data.csv', converters={'career': eval})
    for i in range(0, len(df)):
        name = df.loc[i, 'Name'].split('\\')[1]
        yrs, salaries, notes = data_scraper(name)
        srvtm = df.loc[i, 'SrvTm']
        contracts = delete_dups(merge_lsts(yrs, salaries, change_contract_names(notes)))
        contracts = format_correctly(append_contracts(contracts, srvtm))
        print(contracts)
        contract_lst.append(contracts)
    df['contracts'] = contract_lst
    df.to_csv("Full Team Data & Contracts/" + team + "_data.csv")


team_list = ['diamondbacks', 'braves', 'orioles', 'redsox', 'cubs', 'whitesox', 'reds', 'indians', 'rockies',
             'tigers', 'astros', 'royals', 'angels', 'dodgers', 'marlins', 'brewers', 'twins', 'mets',
             'yankees', 'athletics', 'phillies', 'pirates', 'padres', 'giants', 'mariners', 'cardinals',
             'rays', 'rangers', 'bluejays', 'nationals']


if __name__ == "__main__":
    for team in team_list[6:]:
        construct_contracts(team)