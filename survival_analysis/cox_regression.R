library("survival")

#eps = 1e-16

dead.words <- read.csv(file="dead_words_with_covariates_interpolated.csv",
                       head=TRUE, sep=",")
fit <- coxph(Surv(time1, time2, status) ~ age + kl.score * age
                                          + log.tfidf * age + log.rtf * age,
             data=dead.words)
#             control=coxph.control(eps=eps,
#                                   toler.chol=eps*0.1,
#                                   iter.max=1000000))
print(fit)
