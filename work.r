total = read.csv("total.csv")

# Wins from WAR sum regression
mod <- lm(Wtm ~ WARtot, data=total); summary(mod)
{
  plot(total$WARtot, total$Wtm, col="black"); 
  abline(mod, col="red");
  abline(47, 1, col="blue")
}



