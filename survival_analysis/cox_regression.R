library("survival")

dead.words <- read.csv(file="dead_words_with_kl_interpolated.csv",
                       head=TRUE, sep=",")
fit <- coxph(Surv(time1, time2, status) ~ kl.score, data=dead.words)
print(fit)
