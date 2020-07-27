from player import Player



data1 = []
data2 = []
# for i in range(18, 50):
#     data[str(i)] = []
player1 = Player(1, [0], 24.0, False, 0.0, "")
player2 = Player(1, [0, 0], 20.0, False, 0.0, "")
player3 = Player(1, [0], 23.0, True, .85, "")
player4 = Player(1, [5, 5], 20.0, True, 1.0, "")
players = [player1, player2, player3, player4]
for player in players:
    for j in range(20):
        player.progress()
    print(player.wars)










# print(data2)
# mu, std = norm.fit(data)
#
# # Plot the histogram.
# plt.hist(data, bins=100, density=True, alpha=0.6, color='g')
#
# # Plot the PDF.
# xmin, xmax = plt.xlim()
# x = np.linspace(xmin, xmax, 100)
# p = norm.pdf(x, mu, std)
# title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
# plt.title(title)
#
# plt.show()
# #
# #
# print(data)

# [5.9772988164517535, 5.115640738224641, 6.176086022685363, 6.010856403735656, 6.071251774959499, 5.831671196002827, 5.478261723150831, 5.1967595141012035, 4.928558192698196, 4.6543670593371775, 4.505872486907144, 4.189892286694719, 3.88572799606487, 3.7030399636446347, 3.5308955554638497, 3.421987350187303, 3.3399077027529374, 3.2829004332891336, 3.0516925014434197, 2.949300377290087]