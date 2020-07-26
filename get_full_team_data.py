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

driver = webdriver.Chrome("C:\\Users\\jsimp\\Downloads\\chromedriver_win32\\chromedriver.exe")


def zip_sum(list1, list2):
    sum_list = []
    for (item1, item2) in zip(list1, list2):
        sum_list.append(item1 + item2)
    return sum_list


def extract_age(list):
    list_new = []
    for item in list:
        list_new.append(item.text)
    return list_new


def extract_war(list):
    list_new = []
    for item in list:
        if item.text == '':
            list_new.append(0.0)
        else:
            list_new.append(float(item.text))
    return list_new


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


def data_scraper(name):
    link = "https://www.baseball-reference.com/players/" + name[0] + "/" + name + ".shtml"
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
                tmp1_games = extract_war(tmp.find_elements_by_css_selector('[data-stat="G"]'))
                war_list, age_list = merge_batting_pitching(list(zip(tmp1_age, tmp1)), [])
                games_list, _ = merge_batting_pitching(list(zip(tmp1_age, tmp1_games)), [])
            except selenium.common.exceptions.NoSuchElementException:
                print("no batting stats")
                found = False

    return war_list, games_list, pitcher, start_ratio


def construct_data(team):
    df = pd.read_csv('Team Data/' + team + '-contracts.csv', converters={'career': eval})
    career_wars = []
    positions = []
    games = []
    ratios = []
    for i in range(0, len(df)):
        name = df.loc[i, 'Name'].split('\\')[1]
        wars_list, games_list, pitcher, start_ratio = data_scraper(name)
        print(name, pitcher, start_ratio, wars_list)
        career_wars.append(wars_list)
        positions.append(pitcher)
        ratios.append(start_ratio)
        games.append(games_list)
    df['career'] = pd.Series(career_wars)
    df['pitcher'] = pd.Series(positions)
    df['start_ratio'] = pd.Series(ratios)
    df['games'] = pd.Series(games)
    df.to_csv("Full Team Data/" + team + "_data.csv")


team_list = ['diamondbacks', 'braves', 'orioles', 'redsox', 'cubs', 'whitesox', 'reds', 'indians', 'rockies',
             'tigers', 'astros', 'royals', 'angels', 'dodgers', 'marlins', 'brewers', 'twins', 'mets',
             'yankees', 'athletics', 'phillies', 'pirates', 'padres', 'giants', 'mariners', 'cardinals',
             'rays', 'rangers', 'bluejays', 'nationals']


if __name__ == "__main__":
    for team in team_list:
        construct_data(team)
