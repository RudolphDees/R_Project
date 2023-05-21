date_summary <- read.table("C:\\Users\\Rudy\\Desktop\\Coding_Stuff\\R\\R_Project\\outputs\\date_summary_data.csv", header=TRUE, sep=",")
totalScores <- date_summary$avgTotalScore
bins <- seq(0,13,by=1)
average_total_score_frequency <- cut(totalScores, bins)
table(average_total_score_frequency)
