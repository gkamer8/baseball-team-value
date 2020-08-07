# Statistical analysis that inform simulation constants

# How do we model arbitration?
# Arbitration data is from SPOTRAC

data <- read.csv("arbitration.csv")

data$Salary <- as.numeric(gsub('[$,]', '', data$Salary))

mod <- lm(data$Salary ~ data$WAR + factor(data$Years) + data$Age); summary(mod)

# Alternative with polynomial
mod2 <- lm(data$Salary ~ poly(data$WAR, 3) + factor(data$Years) + data$Age); summary(mod)

plot(data$WAR, data$Salary)

predictor <- predict(mod)

ix <- sort(data$WAR,index.return=T)$ix
lines(data$WAR[ix], predictor[ix], col=2, lwd=2 ) 

plot(predictor, data$Salary)
abline(0, 1)

# Note: model can be improved by using a log transformation
hist(mod$residuals)
qqnorm(mod$residuals)

data <- read.csv("prospect_data/total-board-data.csv")

# How big is the board?

lengths(data)

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

831/472
6 / 3.5

# FV Distribution for J2 signings

prop.table(table(data$FV[data$Sign.Mkt == "J2"]))

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

prop.table(table(data$ETA[data$Sign.Yr == 2020 & data$Age < 20]))  # Age < 20
prop.table(table(data$ETA[data$Sign.Yr == 2020 & data$Age >= 20]))  # Age < 20

# What are the ages of draft prospects?

hist(data$Age[data$Sign.Mkt == "Draft" & data$Sign.Yr == 2020])

# What do the J2 prospects look like?

hist(data$Age[data$Sign.Mkt == "J2" & data$Sign.Yr == 2019])  # Almost all age 17
prop.table(table(data$new.FV[data$Sign.Yr == 2019]))

# What does ETA look like for the whole board?
barplot(table(data$ETA))


# ETA vs. real ETA from The Board

# Adding in actual ETA based on leaderboards

board_2017 = read.csv("ETA Data/2017-board-data.csv")
board_2018 = read.csv("ETA Data/2018-board-data.csv")
leaders_2017 = read.csv("ETA Data/leaders-2017.csv")
leaders_2018 = read.csv("ETA Data/leaders-2018.csv")
leaders_2019 = read.csv("ETA Data/leaders-2019.csv")

board_2017$in2017 <- board_2017$Name %in% leaders_2017$Name
board_2017$in2018 <- board_2017$Name %in% leaders_2018$Name
board_2017$in2019 <- board_2017$Name %in% leaders_2019$Name

board_2018$in2018 <- board_2018$Name %in% leaders_2018$Name
board_2018$in2019 <- board_2018$Name %in% leaders_2019$Name

# Set ETA
{
board_2017$debut <-
  (2017 * board_2017$in2017) + 
  (2018 * (!board_2017$in2017 & board_2017$in2018)) + 
  (2019 * (!board_2017$in2017 & !board_2017$in2018 & board_2017$in2019)) + 
  (2020 * (!board_2017$in2017 & !board_2017$in2018 & !board_2017$in2019))
}

{
  board_2018$debut <-
    (2018 * (board_2018$in2018)) + 
    (2019 * (!board_2018$in2018 & board_2018$in2019)) + 
    (2020 * (!board_2018$in2018 & !board_2018$in2019))
}

# Tables and graphs
tab <- table(board_2017$ETA, board_2017$debut); tab
prop.table(tab, 1)

barplot(table(board_2017$debut[board_2017$ETA == 2017]))
barplot(table(board_2017$debut[board_2017$ETA == 2018]))
barplot(table(board_2017$debut[board_2017$ETA == 2019]))
barplot(table(board_2017$debut[board_2017$ETA > 2019]))

tab <- table(board_2018$ETA, board_2018$debut); tab
prop.table(tab, 1)

barplot(table(board_2018$debut[board_2018$ETA == 2018]))
barplot(table(board_2018$debut[board_2018$ETA == 2019]))
barplot(table(board_2018$debut[board_2018$ETA > 2019]))

# FV Drift

board_2019 = read.csv("ETA Data/2019-board-data.csv")
board_2020 = read.csv("ETA Data/2020-board-data.csv")

total_board <- rbind(data.frame("Name"=board_2017$Name), 
                     data.frame("Name"=board_2018$Name),
                     data.frame("Name"=board_2019$Name),
                     data.frame("Name"=board_2020$Name))
total_board <- unique(total_board)

total_board <- merge(total_board,
                     data.frame("Name"=board_2017$Name,
                                "FV2017"=board_2017$FV), by=c("Name"), all=TRUE)
total_board <- merge(total_board,
                     data.frame("Name"=board_2018$Name,
                                "FV2018"=board_2018$FV), by=c("Name"), all=TRUE)
total_board <- merge(total_board,
                     data.frame("Name"=board_2019$Name,
                                "FV2019"=board_2019$FV), by=c("Name"), all=TRUE)
total_board <- merge(total_board,
                     data.frame("Name"=board_2020$Name,
                                "FV2020"=board_2020$FV), by=c("Name"), all=TRUE)

tab1 <- table(total_board$FV2017, total_board$FV2018); tab1
tab2 <- table(total_board$FV2018, total_board$FV2019); tab2
tab3 <- table(total_board$FV2019, total_board$FV2020); tab3

prop.table(tab1, 1)
prop.table(tab2, 1)
prop.table(tab3, 1)

total = read.csv("total.csv")

# Analysis informing the world series probability function

# Wins from WAR sum regression
mod <- lm(Wtm ~ WARtot, data=total); summary(mod)
{
  plot(total$WARtot, total$Wtm, col="black"); 
  abline(mod, col="red");
  abline(47, 1, col="blue")
}

hist(mod$residuals)
sd(mod$residuals)

