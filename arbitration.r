# Arbitration data is from SPOTRAC

data <- read.csv("arbitration.csv")

data$Salary <- as.numeric(gsub('[$,]', '', data$Salary))

mod <- lm(data$Salary ~ poly(data$WAR, 3) + factor(data$Years) + data$Age); summary(mod)

plot(data$WAR, data$Salary)

predictor <- predict(mod)

ix <- sort(data$WAR,index.return=T)$ix
lines(data$WAR[ix], predictor[ix], col=2, lwd=2 ) 

plot(predictor, data$Salary)
abline(0, 1)
