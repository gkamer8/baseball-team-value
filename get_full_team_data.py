import pandas as pd
import re
import time
import numpy as np
from numpy import random
from datetime import date
from selenium import webdriver
import selenium

"""

This script scrapes data from baseballreference on career war by year,
career games played by year, position, and percent of games started
as pitcher for each player under contract

"""

# driver = webdriver.Chrome("C:\\Users\\jsimp\\Downloads\\chromedriver_win32\\chromedriver.exe")
driver = webdriver.Chrome("/Users/jaredsimpson/Documents/Work/Personal/chromedriver")

start_year = 2021


def zip_sum(list1, list2):
    return [x + y for x,y in zip(list1, list2)]


def extract_age(list):
    return [item.text for item in list]


def extract_war(list):
    list_new = []
    for item in list:
        if item.text == '':
            list_new.append(0.0)
        else:
            list_new.append(float(item.text))
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


def filter_lists(list1):
    list_new = []
    for item in list1:
        age, war = item
        if age != '':
            list_new.append((age, war))
    return list_new


def merge_batting_pitching(list1, list2):
    list1 = filter_lists(list1)
    list2 = filter_lists(list2)
    dict1 = {}
    for (age, war) in (list1 + list2):
        if age in dict1:
            dict1[age] = dict1[age] + war
        else:
            dict1[age] = war
    dictionary_items = dict1.items()
    sorted_items = sorted(dictionary_items)
    return list(list(zip(*sorted_items))[1]), list(list(zip(*sorted_items))[0])


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
    return [(yr, sal, nt) for (yr, sal, nt) in lst if yr >= start_year]


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





def data_scraper(name):
    print(name)
    link = "https://www.baseball-reference.com/players/" + name[0] + "/" + name + ".shtml"
    driver.get(link)
    war_list = []
    games_list = []
    pitcher = False
    found = True
    start_ratio = ''
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


    try:
        position = driver.find_element_by_xpath("//div[@id='meta']/div[2]/p").text
    except selenium.common.exceptions.NoSuchElementException:
        print("Failed to find position")
        found = False
    else:
        if position == "Position: Pitcher":
            print("found pitcher")
            pitcher = True

    if found:
        if pitcher:
            try:
                tmp = driver.find_element_by_id('pitching_value').find_element_by_tag_name('tbody')
                tmp1 = extract_war(tmp.find_elements_by_css_selector('[data-stat="WAR_pitch"]'))
                tmp1_age = extract_age(tmp.find_elements_by_css_selector('[data-stat="age"]'))
                tmp1_games = extract_war(tmp.find_elements_by_css_selector('[data-stat="G"]'))
                tmp1_years = extract_year(tmp.find_elements_by_css_selector('[data-stat="year_ID"]'))
                career_years = list(set(tmp1_years))
                career_years = [x for x in career_years if x != 0]
                career_years.sort()
                g_temp = driver.find_element_by_class_name('stats_pullout')
                gs = g_temp.find_element_by_xpath("//div[@id='info']/div[4]/div[3]/div[2]/p").text
                gp = g_temp.find_element_by_xpath("//div[@id='info']/div[4]/div[3]/div/p").text
                start_ratio = float(gs) / float(gp)
            except selenium.common.exceptions.NoSuchElementException:
                print("no pitching stats")
            else:
                try:
                    tmp = driver.find_element_by_id('batting_value').find_element_by_tag_name('tbody')
                    tmp2 = extract_war(tmp.find_elements_by_css_selector('[data-stat="WAR"]'))
                    tmp2_age = extract_age(tmp.find_elements_by_css_selector('[data-stat="age"]'))
                    war_list, age_list = merge_batting_pitching(list(zip(tmp1_age, tmp1)), list(zip(tmp2_age, tmp2)))
                    games_list, _ = merge_batting_pitching(list(zip(tmp1_age, tmp1_games)), [])
                except selenium.common.exceptions.NoSuchElementException:
                    print("pitching only")
                    war_list, age_list = merge_batting_pitching(list(zip(tmp1_age, tmp1)), [])
                    games_list, _ = merge_batting_pitching(list(zip(tmp1_age, tmp1_games)), [])
        else:
            try:
                tmp = driver.find_element_by_id('batting_value').find_element_by_tag_name('tbody')
                tmp1 = extract_war(tmp.find_elements_by_css_selector('[data-stat="WAR"]'))
                tmp1_age = extract_age(tmp.find_elements_by_css_selector('[data-stat="age"]'))
                tmp1_years = extract_year(tmp.find_elements_by_css_selector('[data-stat="year_ID"]'))
                career_years = list(set(tmp1_years))
                career_years = [x for x in career_years if x != 0]
                career_years.sort()
                tmp1_games = extract_war(tmp.find_elements_by_css_selector('[data-stat="G"]'))
                war_list, age_list = merge_batting_pitching(list(zip(tmp1_age, tmp1)), [])
                games_list, _ = merge_batting_pitching(list(zip(tmp1_age, tmp1_games)), [])
            except selenium.common.exceptions.NoSuchElementException:
                print("no batting stats")

    return war_list, games_list, pitcher, start_ratio, career_years, yrs, salaries, notes


def construct_data(team):
    df = pd.read_csv('Team Data/' + team + '-contracts.csv', converters={'career': eval})
    career_wars = []
    positions = []
    games = []
    ratios = []
    years = []
    contracts = []
    for i in range(0, len(df)):
        name = df.loc[i, 'Name'].split('\\')[1]
        wars_list, games_list, pitcher, start_ratio, contract_years, sal_yrs, salaries, notes = data_scraper(name)
        print(name, pitcher, start_ratio, wars_list, contract_years)
        career_wars.append(wars_list)
        positions.append(pitcher)
        ratios.append(start_ratio)
        games.append(games_list)
        srvtm = df.loc[i, 'SrvTm']
        sals = delete_dups(merge_lsts(sal_yrs, salaries, change_contract_names(notes)))
        sals = format_correctly(append_contracts(sals, srvtm))
        contracts.append(sals)
        years.append(contract_years)
    df['career'] = pd.Series(career_wars)
    df['games'] = pd.Series(games)
    df['contracts'] = pd.Series(contracts)
    df['years'] = pd.Series(years)
    df['pitcher'] = pd.Series(positions)
    df['start_ratio'] = pd.Series(ratios)

    df.to_csv("Full Team Data & Contracts/" + team + "_data.csv")


team_list = ['diamondbacks', 'braves', 'orioles', 'redsox', 'cubs', 'whitesox', 'reds', 'indians', 'rockies',
             'tigers', 'astros', 'royals', 'angels', 'dodgers', 'marlins', 'brewers', 'twins', 'mets',
             'yankees', 'athletics', 'phillies', 'pirates', 'padres', 'giants', 'mariners', 'cardinals',
             'rays', 'rangers', 'bluejays', 'nationals']


if __name__ == "__main__":
    for team in team_list:
        construct_data(team)
