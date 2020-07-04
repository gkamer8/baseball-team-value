csv1 = read.csv("Batting/00-04.csv")
csv2 = read.csv("Batting/05-09.csv")
csv3 = read.csv("Batting/10-14.csv")
csv4 = read.csv("Batting/15-19.csv")

csv5 = read.csv("Pitching/00-04.csv")
csv6 = read.csv("Pitching/05-09.csv")
csv7 = read.csv("Pitching/10-14.csv")
csv8 = read.csv("Pitching/15-19.csv")

total = rbind(csv1, csv2);
total <- rbind(total, csv3)
total <- rbind(total, csv4)

batting <- data.frame("Year"=total$Year, "Tm"=total$Tm, "Wtm"=total$Wtm, "Ltm"=total$Ltm, "tmWL"=total$tmW.L., "G"=total$G, "WARbat"=total$WAR)

head(batting)

total = rbind(csv5, csv6);
total <- rbind(total, csv7)
total <- rbind(total, csv8)

pitching <- data.frame("Year"=total$Year, "Tm"=total$Tm, "WARpit"=total$WAR)

total <- merge(batting, pitching, by=c("Year", "Tm"))

total$WARtot <- total$WARbat + total$WARpit

write.csv(total, "total.csv")
