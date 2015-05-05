library("survival")

dead.words <- read.csv(file="dead_words_with_covariates_interpolated.csv",
                       head=TRUE, sep=",")
fit <- coxph(Surv(time1, time2, status) ~ kl.score + tfidf, data=dead.words)
print(fit)
