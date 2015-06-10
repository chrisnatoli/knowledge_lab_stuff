library("survival")



dead.words <- read.csv(file="dead_words_with_covariates_interpolated.csv",
                       head=TRUE, sep=",")
dead.words <- na.omit(dead.words) # Remove rows with missing data.

# Transform some variables.
dead.words$log.tfidf = log(dead.words$tfidf)
dead.words$log.rtf = log(dead.words$rtf)
dead.words$centered.tfidf = ((dead.words$tfidf - mean(dead.words$tfidf))
                             /sd(dead.words$tfidf))
dead.words$centered.rtf = ((dead.words$rtf - mean(dead.words$rtf))
                             /sd(dead.words$rtf))
dead.words$sqrt.age = sqrt(dead.words$age)



# Run some cox regressions and keep the last one in memory.
cat("LARGE MODEL\n")
fit <- coxph(Surv(time1, time2, status) ~ sqrt.age + kl.score * sqrt.age
                                          + centered.tfidf * sqrt.age
                                          + centered.rtf * sqrt.age
                                          + kl.score:centered.tfidf
                                          + kl.score:centered.rtf
                                          + centered.tfidf:centered.rtf,
             data=dead.words, control = coxph.control(iter.max = 1e6))
print(fit)
large_model_loglik <- summary(fit)$loglik[2]
large_model_df <- summary(fit)$logtest[2]

cat("\n\nSMALL MODEL\n")
fit <- coxph(Surv(time1, time2, status) ~ sqrt.age + kl.score * sqrt.age
                                          + centered.tfidf * sqrt.age
                                          + centered.rtf * sqrt.age,
             data=dead.words, control = coxph.control(iter.max = 1e7))
print(fit)

cat("\n\nDIAGNOSTICS\n")
cat(sprintf("Cox & Snell pseudo-R^2 = %f; max possible R^2 = %f\n",
            summary(fit)$rsq[1], summary(fit)$rsq[2]))
cat(sprintf("Normalization: Cox & Snell R^2 / max possible R^2 = %f\n\n",
            summary(fit)$rsq[1] / summary(fit)$rsq[2]))
#cat(sprintf("AIC = %f\n", extractAIC(fit)[2]))
small_model_loglik <- summary(fit)$loglik[2]
small_model_df <- summary(fit)$logtest[2]
deviance <- -2 * (small_model_loglik - large_model_loglik)
pvalue <- 1 - pchisq(deviance, df=large_model_df - small_model_df)
cat(sprintf("Under H_0 where small model is as good as large model, p = %f\n\n",
            pvalue))



# Compute the suggested sample size a la Peduzzi et al.,
# "Importance of events per independent variable in proportional hazards
# regression analysis" (1995).
sample_size = length(unique(dead.words$word))
num_predictors = length(fit$coefficients)
num_deaths = sum(dead.words$status)
num_censored = sample_size - num_deaths
p = min(num_deaths, num_censored) / (num_deaths + num_censored)
suggested_sample_size = 10 * num_predictors / p
cat(sprintf("Sample size is %d; suggested sample size is %f.\n\n",
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
