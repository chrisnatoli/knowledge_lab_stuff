library("survival")



dead.words <- read.csv(file="dead_words_with_covariates_interpolated.csv",
                       head=TRUE, sep=",")


fit <- coxph(Surv(time1, time2, status) ~ age + kl.score * age
                                          + log.tfidf * age + log.rtf * age,
             data=dead.words)
print(fit)


residuals <- residuals(fit, type="martingale", collapse=dead.words$word)


# Get tuples of words with their time origins.
origins <- unique(dead.words[c("word", "time.origin")])
origins$time.origin <- as.Date(paste(as.character(origins$time.origin),
                                     "-1", sep=""),
                               "%Y-%m-%d") # Convert string to date.
row.names(origins) <- origins$word # Rename rows by word.
xy.pairs <- cbind(origins, residuals)#[c("time.origin", "residuals")]
xy.pairs <- xy.pairs[with(xy.pairs, order(time.origin)), ] # Sort.


# Split the dataset into "outliers" and the rest so that I can
# label only the outliers.
outliers <- subset(xy.pairs, abs(residuals) > 0.75)
nonoutliers <- xy.pairs[!(xy.pairs$word %in% outliers$word), ]


png(filename="martingale_residuals.png")
plot(outliers$time.origin, outliers$residuals,
     xlab="Time origin", ylab="Martingale residual")
abline(0,0)
text(outliers$time.origin, outliers$residuals+0.1, row.names(outliers))
points(nonoutliers$time.origin, nonoutliers$residuals)
#axis(side=1, at=c(seq(from=1976,
#                      to=max(as.numeric(format(origins$time.origin, "%Y"))),
#                      by=2)))
dev.off()
