from data import divisions_dict, won_division, made_playoffs
import matplotlib.pyplot as plt
import numpy as np
import math

if __name__ == "__main__":
    
    percent_won_division = []
    wl_percentages = np.linspace(0, 1, 600)

    for t in wl_percentages:
        times_won = 0
        total_tries = 0
        for y in range(2000, 2020):
            for d in range(6):
                my_name = ""
                for k in divisions_dict:
                    if divisions_dict[k] == d:
                        my_name = k
                        break

                l = 'NL'
                if d < 3:
                    l = "AL"

                fake_team = {
                    'name': my_name,
                    'year': y,
                    'wl': t,
                    'league': l
                }

                if won_division(fake_team):
                    times_won += 1
                total_tries += 1
        p = times_won / total_tries

        percent_won_division.append(p)

    domain = np.linspace(0, 1, 600)
    my_range = []
    for x in domain:
        my_range.append(1 / (1 + math.exp(-1 *(-31 + (53 * x)))))

    percent_made_ploffs = []
    wl_percentages = np.linspace(0, 1, 200)

    for t in wl_percentages:
        times_won = 0
        total_tries = 0
        for y in range(2000, 2020):
            for d in range(6):
                my_name = ""
                for k in divisions_dict:
                    if divisions_dict[k] == d:
                        my_name = k
                        break

                l = 'NL'
                if d < 3:
                    l = "AL"

                fake_team = {
                    'name': my_name,
                    'year': y,
                    'wl': t,
                    'league': l
                }

                if made_playoffs(fake_team):
                    times_won += 1
                total_tries += 1
        p = times_won / total_tries

        percent_made_ploffs.append(p)

    domain = np.linspace(0, 1, 600)
    new_range = []
    for x in domain:
        new_range.append(1 / (1 + math.exp(-1 *(-54.7 + (100 * x)))))

    plt.plot(domain.reshape(-1, 1), np.array(my_range).reshape(-1, 1), color="r", label="y = 1 / (1 + exp(-(-31 + 53x)))")

    plt.plot(domain.reshape(-1, 1), np.array(percent_won_division).reshape(-1, 1), label="Historical Probabilities - Won Division")

    plt.plot(domain.reshape(-1, 1), np.array(new_range).reshape(-1, 1),label="y = 1 / (1 + exp(-(-54.7 + 100x)))")

    plt.plot(wl_percentages.reshape(-1, 1), np.array(percent_made_ploffs).reshape(-1, 1), color="y",  label="Historical Probabilities - Made Playoffs")

    plt.ylabel("Probability")
    plt.xlabel("W-L%")
    plt.legend()
    plt.show()