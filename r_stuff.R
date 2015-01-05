library(diptest)
library(boot)

KLs <- scan('tmp/all_KLs')
means <- scan('tmp/all_KL_means')
stddevs <- scan('tmp/all_KL_stddevs')
KLs_subset <- KLs[KLs > 1]

dip.test(KLs)
dip.test(KLs_subset)
dip.test(means)
dip.test(stddevs)

mean.with.indices <- function(dat, idx) mean(dat[idx], na.rm = TRUE)
boot(data=KLs, statistic=mean.with.indices, R=1000)
mean(KLs)
