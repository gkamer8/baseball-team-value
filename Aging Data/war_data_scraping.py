import os
import re
import time
import pandas as pd
import numpy as np
from numpy import random
from datetime import date
from selenium import webdriver


def data_scraper(players_list, batting):
    df_lst = []
    # open a web browser
    driver = webdriver.Chrome("C:\\Users\\jsimp\\Downloads\\chromedriver_win32\\chromedriver.exe")
    for name in players_list:
        print(name)
        try:
            link = "https://www.baseball-reference.com/players/" + name[1][0] + "/" + name[1][:5] + name[0][:2] + "01.shtml"
            driver.get(link)
            if batting:
                tmp = driver.find_element_by_id('batting_value')
                tmp1 = tmp.find_elements_by_css_selector('[data-stat="WAR"]')
                tmp2 = tmp.find_elements_by_css_selector('[data-stat="age"]')
            else:
                tmp = driver.find_element_by_id('pitching_value')
                tmp1 = tmp.find_elements_by_css_selector('[data-stat="WAR_pitch"]')
                tmp2 = tmp.find_elements_by_css_selector('[data-stat="age"]')
        except:
            try:
                link = "https://www.baseball-reference.com/players/" + name[1][0] + "/" + name[1][:5] + name[0][:2] + "02.shtml"
                driver.get(link)
                if batting:
                    tmp = driver.find_element_by_id('batting_value')
                    tmp1 = tmp.find_elements_by_css_selector('[data-stat="WAR"]')
                    tmp2 = tmp.find_elements_by_css_selector('[data-stat="age"]')
                else:
                    tmp = driver.find_element_by_id('pitching_value')
                    tmp1 = tmp.find_elements_by_css_selector('[data-stat="WAR_pitch"]')
                    tmp2 = tmp.find_elements_by_css_selector('[data-stat="age"]')
            except:
                print("FAILED")
        else:
            war_list = []
            age_list = []
            for i in range(1, len(tmp2)):
                war_list.append(tmp1[i].text)
                age_list.append(tmp2[i].text)
            age_list.append("")
            war_list.append("")
            print(war_list)
            print(age_list)
            df_lst.append(pd.DataFrame(list(zip(war_list, age_list)),
                                       columns=['WAR', 'Age']))

        time.sleep(min(2, (3 * abs(random.standard_normal(1)))[0]))

    main_df = pd.concat(df_lst)
    return main_df


def format_player_list(players):
    players = np.array(players)
    players = (np.unique(players)).tolist()
    player_names = list(map(lambda x: re.sub(r'[^\w\s]', '', x), players))
    player_names = list(map(lambda x: x.lower().split(" "), player_names))
    return player_names


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

print(len(pitchers))
print(len(batters))

# batters_df = data_scraper(format_player_list(batters), True)
# batters_df.to_csv('Batters_WAR_by_Age.csv')

pitchers_df = data_scraper(format_player_list(pitchers), False)
pitchers_df.to_csv('Pitchers_WAR_by_Age.csv')

