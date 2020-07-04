# Baseball Team Value

This project is an effort to describe a baseball team's value in terms of discounted future championships. 

## Project Organization

**Batting and Pitching Folder**: Team data (including team stats and results) since 2000 (going farther back introduces problems with the expansion era and different playoff systems) are located in the Batting and Pitching folders. 

**Playoffs**: The Playoffs folder contains a CSV with the results of every playoff round since 2012, the first year of the WC game format.

**data.py**: In order to load and evaluate that data, data.py provides some simple functions such as load_data(), which creates a list of teams with WAR and record, in addition to functions to determine whether teams made the playoffs and how.

**war_wl.py**: If run as main, displays graphs of the relationship between WAR and W/L%. Contains get_war_wl_regr(), which returns an sklearn regression object for the relationship between WAR and W/L%. Contains get_war_wl_resids(), which returns a list of residuals.

**ws_result_and_WAR.py**: If run as main, displays graphs of the relationship between winning the world series and regular season war among teams that make it to the divisional round.

**wl_percentage_and_division_or_wc.py**: If run as main, takes a while to display functions turning wins into playoff / division-win odds.