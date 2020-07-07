total = read.csv("total.csv")

# Wins from WAR sum regression
mod <- lm(Wtm ~ WARtot, data=total); summary(mod)
{
  plot(total$WARtot, total$Wtm, col="black"); 
  abline(mod, col="red");
  abline(47, 1, col="blue")
}

# ETA vs. real ETA

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

# Development matrix by inspection

development_matrix <- matrix(
  c(
    1, .75, .25, .05, .01, .01, 0,
    0, .15, .35, .25, .05, .01, 0,
    0,   0, .30, .35, .25, .05, 0,
    0,   0,   0, .25, .35, .25, 0,
    0,   0,   0,   0, .24, .35, 0,
    0,   0,   0,   0,   0, .23, 0,
    0,  .1,  .1,  .1, .1,  .1,  1
  ),
  nrow=7,
  ncol=7,
  byrow=TRUE
)
t(development_matrix)

library(expm) 
(development_matrix %^% 100) %*% c(0, 0, 0, 1, 0, 0, 0)

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

# Roughly: 
# Stay probabililty: 30-50
# Up/down one:       15-35
# Up/down two:        5-15

