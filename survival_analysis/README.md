knowledge_lab_stuff/survival_analysis
=====================================

Note that these scripts expect the directory above `new_word_kl_analysis/` to have another subdirectory called "data" containg PubMed abstracts, KL score data, TFIDF data, and RTF data.

#### `find_dead_words.py`

Looks for words that die in the corpus. A word is considered to have died if
* it doesn't appear before 1976,
* it doesn't occur during r after a cutoff year of 2005,
* it exists for a streak of n consecutive years (where n depends on the settings, but is usually between 1 and 5),
* it contains at least one alphabet character in it,
* it has a minimum term frequency after 1976 of 20,
* it has a minimum document frequency (where a document is a collection of abstracts for a given month in a given year) of 12,
* it isn't absent for a gap longer than m months (where m=12 or m=18).

This script outputs `dead_words_streakX_tfY_dfZ.csv` where rows are words and the columns are the word itself, the time origin (i.e., its first appearance), and its end point (i.e., its last appearance). This script should be run on a supercomputer.

#### `attach_covariates.py`

Adds KL score data, TFIDF data, and RTF data  to the csv file of dead words. Note that the text preprocessing I used is different from the preprocessing used to get KL, TFIDF, and RTF data, so some words don't have much KL score data. These words are omitted from the final dataset; many dead words are lost this way. This script also linearly interpolates the KL score, TFIDF, and RTF data across any gaps, as recommended by Collett's textbook "Modelling Survival Analysis in Medical Research". The data is then written to file in a special way so that it will be easy to plug into R's Cox regression function. The output file is `dead_words_with_covariates.csv`.

#### `cox_regression.R`

Estimates a couple Cox regression models to determine the effects of certain covariates, namely, age, KL score, TFIDF, RTF, and certain interaction terms. It also checks some diagnostics, including Cox & Snell pseudo-R^2, a deviance score test between the two (nested) regression models, an estimation of an appropriate sample size, and a plot of the martingale residuals with outliers labeled.
