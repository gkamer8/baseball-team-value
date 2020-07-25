import os
import re
import time
import pandas as pd
import numpy as np
from numpy import random
from datetime import date
from selenium import webdriver
from get_full_team_data import zip_sum, extract_age, extract_war, filter_lists, driver
import selenium


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


def data_scraper(name):
    link = "https://www.baseball-reference.com/players/" + name[1][0] + "/" + name[1][:5] + name[0][:2] + "01.shtml"
    driver.get(link)
    war_list = []
    age_list = []
    games_list = []
    pitcher = False
    found = True
    print(name)
    start_ratio = ''
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
                g_temp = driver.find_element_by_class_name('stats_pullout')
                gs = g_temp.find_element_by_xpath("//div[@id='info']/div[4]/div[3]/div[2]/p").text
                gp = g_temp.find_element_by_xpath("//div[@id='info']/div[4]/div[3]/div/p").text
                start_ratio = float(gs) / float(gp)
            except selenium.common.exceptions.NoSuchElementException:
                print("no pitching stats")
                found = False
            else:
                try:
                    tmp = driver.find_element_by_id('batting_value').find_element_by_tag_name('tbody')
                    tmp2 = extract_war(tmp.find_elements_by_css_selector('[data-stat="WAR"]'))
                    tmp2_age = extract_age(tmp.find_elements_by_css_selector('[data-stat="age"]'))
                    war_list, age_list= merge_batting_pitching(list(zip(tmp1_age, tmp1)), list(zip(tmp2_age, tmp2)))
                    games_list, _ = merge_batting_pitching(list(zip(tmp1_age, tmp1_games)), [])
                except selenium.common.exceptions.NoSuchElementException:
                    print("pitching only")
                    war_list, age_list= merge_batting_pitching(list(zip(tmp1_age, tmp1)), [])
                    games_list, _ = merge_batting_pitching(list(zip(tmp1_age, tmp1_games)), [])
        else:
            try:
                tmp = driver.find_element_by_id('batting_value').find_element_by_tag_name('tbody')
                tmp1 = extract_war(tmp.find_elements_by_css_selector('[data-stat="WAR"]'))
                tmp1_age = extract_age(tmp.find_elements_by_css_selector('[data-stat="age"]'))
                tmp1_games = extract_war(tmp.find_elements_by_css_selector('[data-stat="G"]'))
                war_list, age_list = merge_batting_pitching(list(zip(tmp1_age, tmp1)), [])
                games_list, _ = merge_batting_pitching(list(zip(tmp1_age, tmp1_games)), [])
            except selenium.common.exceptions.NoSuchElementException:
                print("no batting stats")
                found = False

    return war_list, age_list, games_list, pitcher, start_ratio, found

# Takes a list of names and formats it for construction of urls
def format_player_list(players):
    players = np.array(players)
    players = (np.unique(players)).tolist()
    player_names = list(map(lambda x: re.sub(r'[^\w\s]', '', x), players))
    player_names = list(map(lambda x: x.lower().split(" "), player_names))
    return player_names


# Takes player names from csvs, merges into one list, and eliminates duplicates
batters2020 = pd.read_csv('Aging Data\\mlb-player-stats-Batters2020.csv')
batters2020 = batters2020['Player'].to_list()
batters2015 = pd.read_csv('Aging Data\\mlb-player-stats-Batters2015.csv')
batters2015 = batters2015['Player'].to_list()
batters2010 = pd.read_csv('Aging Data\\mlb-player-stats-Batters2010.csv')
batters2010 = batters2010['Player'].to_list()
batters2005 = pd.read_csv('Aging Data\\mlb-player-stats-Batters2005.csv')
batters2005 = batters2005['Name'].to_list()
batters2000 = pd.read_csv('Aging Data\\mlb-player-stats-Batters2000.csv')
batters2000 = batters2000['Name'].to_list()
batters = batters2020 + batters2015 + batters2010 + batters2005 + batters2000

pitchers2020 = pd.read_csv('Aging Data\\mlb-player-stats-Pitchers2020.csv')
pitchers2020 = pitchers2020['Player'].to_list()
pitchers2015 = pd.read_csv('Aging Data\\mlb-player-stats-Pitchers2015.csv')
pitchers2015 = pitchers2015['Player'].to_list()
pitchers2010 = pd.read_csv('Aging Data\\mlb-player-stats-Pitchers2010.csv')
pitchers2010 = pitchers2010['Player'].to_list()
pitchers2005 = pd.read_csv('Aging Data\\mlb-player-stats-Pitchers2005.csv')
pitchers2005 = pitchers2005['Name'].to_list()
pitchers2000 = pd.read_csv('Aging Data\\mlb-player-stats-Pitchers2000.csv')
pitchers2000 = pitchers2000['Name'].to_list()
pitchers = pitchers2020 + pitchers2015 + pitchers2010 + pitchers2005 + pitchers2000

players = batters + pitchers
# Stores scraped WAR data in csvs
# batters_df = data_scraper(format_player_list(batters), True)
# batters_df.to_csv('Aging Data\\Batters_WAR_by_Age.csv')
#
# pitchers_df = data_scraper(format_player_list(pitchers), False)
# pitchers_df.to_csv('Aging Data\\Pitchers_WAR_by_Age.csv')


def get_data(name_list):
    ages = []
    wars = []
    games = []
    pitchers = []
    start_ratios = []
    for name in format_player_list(name_list):
        war_lst, age_lst, games_lst, pitcher, start_ratio, found = data_scraper(name)
        if found:
            wars.append(war_lst)
            ages.append(age_lst)
            games.append(games_lst)
            pitchers.append(pitcher)
            start_ratios.append(start_ratio)
    return ages, wars, games, pitchers, start_ratios

if __name__ == "__main__":
    ages1, wars1, games, positions, ratios = get_data(players)
    df_b = pd.DataFrame(list(zip(wars1, ages1, games, positions, ratios)),
                   columns =['WAR', 'Age', 'Games', 'pitcher', 'start_ratio'])
    df_b.to_csv('Aging Data/WAR_by_Age1.csv')

