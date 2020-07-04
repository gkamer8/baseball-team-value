from data import *
import matplotlib.pyplot as plt
import numpy as np
from sklearn import linear_model
import scipy.stats as stats
import math


# Returns sklearn regression object
def get_war_wl_regr():
    data = load_data()

    # Create np arrays
    x = []
    y = []
    for d in data:
        x.append([d['war']])
        y.append([d['wl']])

    X = np.array(x)
    y = np.array(y)

    # Fit regression line
    regr = linear_model.LinearRegression()
    regr.fit(X, y)

    return regr

# Returns list of residuals
def get_war_wl_resids():
    
    resids = []
    for x in range(len(y)):
        resids.append(y_pred[x] - y[x])

    resids = np.array(resids)

    return resids

# Creates graphs
# Includes duplicate code
if __name__ == "__main__":
    data = load_data()

    # Create np arrays
    x = []
    y = []
    for d in data:
        x.append([d['war']])
        y.append([d['wl']])

    X = np.array(x)
    y = np.array(y)

    # Fit regression line
    regr = linear_model.LinearRegression()
    regr.fit(X, y)

    print("War/wl regression fit: " + str(round(regr.score(X, y), 3)))

    y_pred = regr.predict(X)

    # Plot scatter of actual data
    plt.scatter(x, y)

    # Plot fit line
    plt.plot(x, y_pred, color='r', label='y = 0.00588x + 0.30438')

    plt.ylabel('W-L%')
    plt.xlabel('Team WAR')
    plt.legend()
    plt.show()

    # Find the distribution of the residuals

    resids = []
    for x in range(len(y)):
        resids.append(y_pred[x] - y[x])

    resids = np.array(resids)

    mu = 0
    variance = np.var(resids)
    sigma = math.sqrt(variance)
    x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)

    plt.plot(x, stats.norm.pdf(x, mu, sigma))
    plt.scatter(resids, np.random.normal(0,.3,600), marker=".", color='r')
    plt.ylabel('Probability density')
    plt.xlabel('Predicted WL% - actual WL%')
    plt.show()

    print("y = " + str(round(regr.coef_[0][0], 5)) + "x + " + str(round(regr.intercept_[0], 5)))

    print("Residual mean: " + str(np.mean(resids)))
    print("Residual variance: " + str(np.var(resids)))