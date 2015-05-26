library("survival")



dead.words <- read.csv(file="dead_words_with_covariates_interpolated.csv",
                       head=TRUE, sep=",")


# Transform some variables.
dead.words$log.tfidf = log(dead.words$tfidf)
dead.words$log.rtf = log(dead.words$rtf)
dead.words$centered.tfidf = ((dead.words$tfidf - mean(dead.words$tfidf))
                             /sd(dead.words$tfidf))
dead.words$centered.rtf = ((dead.words$rtf - mean(dead.words$rtf))
                             /sd(dead.words$rtf))
dead.words$sqrt.age = sqrt(dead.words$age)



# Run some cox regressions and keep the last one in memory.
coxph(Surv(time1, time2, status) ~ sqrt.age + kl.score * sqrt.age
                                   + log.tfidf * sqrt.age
                                   + log.rtf * sqrt.age,
             data=dead.words)
coxph(Surv(time1, time2, status) ~ sqrt.age + kl.score * sqrt.age
                                   + centered.tfidf * sqrt.age
                                   + centered.rtf * sqrt.age
                                   + kl.score:centered.tfidf
                                   + kl.score:centered.rtf
                                   + centered.tfidf:centered.rtf,
             data=dead.words)
fit <- coxph(Surv(time1, time2, status) ~ sqrt.age + kl.score * sqrt.age
                                          + centered.tfidf * sqrt.age
                                          + centered.rtf * sqrt.age,
             data=dead.words)
print(fit)



# Compute the suggested sample size a la Peduzzi et al.,
# "Importance of events per independent variable in proportional hazards
# regression analysis" (1995).
sample_size = length(unique(dead.words$word))
num_predictors = length(fit$coefficients)
num_deaths = sum(dead.words$status)
num_censored = sample_size - num_deaths
p = min(num_deaths, num_censored) / (num_deaths + num_censored)
suggested_sample_size = 10 * num_predictors / p
cat(sprintf("Sample size is %d; suggested sample size is %f.\n",
            sample_size, suggested_sample_size))



# Make a martingale residual plot.
residuals <- residuals(fit, type="martingale", collapse=dead.words$word)

# Get tuples of words with their time origins.
origins <- unique(dead.words[c("word", "time.origin")])
origins$time.origin <- as.Date(paste(as.character(origins$time.origin),
                                     "-1", sep=""),
                               "%Y-%m-%d") # Convert string to date.
row.names(origins) <- origins$word # Rename rows by word.
xy.pairs <- cbind(origins, residuals)
xy.pairs <- xy.pairs[with(xy.pairs, order(time.origin)), ] # Sort.

# Split the dataset into "outliers" and the rest so that I can
# label only the outliers.
outliers <- subset(xy.pairs, abs(residuals) > 0.75)
nonoutliers <- xy.pairs[!(xy.pairs$word %in% outliers$word), ]

# Plot outliers first, add labels, then plot the rest.
png(filename="martingale_residuals.png")
plot(outliers$time.origin, outliers$residuals,
     xlab="Time origin", ylab="Martingale residual",
     xlim=c(as.Date("1975-1-1", "%Y-%m-%d"),
            as.Date("2000-1-1", "%Y-%m-%d")))
text(outliers$time.origin, outliers$residuals, row.names(outliers),
     cex=0.7, pos=4, offset=0.5)
points(nonoutliers$time.origin, nonoutliers$residuals)
abline(0,0)
dev.off()
