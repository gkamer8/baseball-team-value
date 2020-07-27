data <- read.csv("prospect_data/total-board-data.csv")

# How many prospects per draft?
picks_2020 <- data[data$Sign.Mkt == "Draft" & data$Sign.Yr == 2020,]
lengths(picks_2020)[1]; 124 / 30  # There are 124 from 2020 - not all have signed yet, though, and the draft was smaller

picks_2019 <- data[data$Sign.Mkt == "Draft" & data$Sign.Yr == 2019,]
lengths(picks_2019)[1]; 184 / 30  # There are 184 from 2019

picks_2018 <- data[data$Sign.Mkt == "Draft" & data$Sign.Yr == 2018,]
lengths(picks_2018)[1]; 174 / 30  # There are 174 in 2018 - expected, because some drop out

# What proportion of prospects are from J2 vs. the Draft?

table(data$Sign.Mkt)
print("From J2: "); 472 / (831 + 472)
print("From Draft: "); 831 / (831 + 472)

# What is the FV distribution for a draft year?

# 2019
picks_2019$new.FV <- strtoi(gsub("+", "", picks_2019$FV))
table(picks_2019$new.FV)
prop.table(table(picks_2019$new.FV))
barplot(table(picks_2019$new.FV))

# 2018
picks_2018$new.FV <- strtoi(gsub("+", "", picks_2018$FV))
table(picks_2018$new.FV)
prop.table(table(picks_2018$new.FV))
barplot(table(picks_2018$new.FV))

# What are the FVs for each draft slot, assuming a draft of 180 players?
# Using figures from 2019 draft

.0109 * 180  # Top two are 60
.0326 * 180  # Next 6 are 55
.0435 * 180  # Next 8 are 50
.2283 * 180  # Next 41 are 45
.6848 * 180  # Next 123 are 40
2 + 6 + 8 + 41 + 123

# How many prospects are pitchers vs. hitters?

prop.table(table(data$Pos))
.100 + .393  # Pitchers - it's about evenly split

# What's the distribution of WL%?

wl.data <- read.csv("total.csv")
hist(wl.data$tmWL)

# Per year - it's pretty erratic
hist(wl.data[wl.data$Year == 2019,]$tmWL)
hist(wl.data[wl.data$Year == 2018,]$tmWL)
hist(wl.data[wl.data$Year == 2017,]$tmWL)
hist(wl.data[wl.data$Year == 2016,]$tmWL)

# What are the cut-off values for the important draft picks?

quantile(wl.data$tmWL, probs = c(2/30, 8/30, 16/30, (57 - 30)/30))

# What's the ETA of prospects when they're signed?

prop.table(table(data$ETA[data$Sign.Yr == 2020]))
prop.table(table(data$ETA[data$Sign.Yr == 2019]))
prop.table(table(data$ETA[data$Sign.Yr == 2018]))

plot(data$ETA[data$Sign.Yr == 2020], data$Age[data$Sign.Yr == 2020])

# What are the ages of draft prospects?

hist(data$Age[data$Sign.Mkt == "Draft" & data$Sign.Yr == 2020])

# What do the J2 prospects look like?

hist(data$Age[data$Sign.Mkt == "J2" & data$Sign.Yr == 2019])  # Almost all age 17
prop.table(table(data$new.FV[data$Sign.Yr == 2019]))
