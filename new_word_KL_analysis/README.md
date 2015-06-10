knowledge_lab_stuff/new_word_KL_analysis
========================================

Note that these scripts expect the directory above new_word_kl_analysis/ to have another subdirectory called "data" containg PubMed abstracts and KL score data.

### `find_new_words.py`

Looks for new words in the corpus of abstracts. A word is considered "new" if
* it doesn't occur before 1970,
* it occurs before 2000,
* it is present in at least 80% or 90% (80% and 90% are called the "density") of the documents, where a document in this case is a collection of all abstracts in a given month in a given year,
* it contains at least one alphabet character in it,
* it doesn't contain the string `year-old`.
This script outputs `new_words_0.8density.csv` or `new_words_0.8density.csv`, which is a table where rows are words and the columns are the the word itself, its first appearance, the number of months it appeared in, its term frequency over the entire corpus, and its relative term frequency. This script should be run on a supercomputer.

### `find_old_words.py`

Looks for old words in the corpus of abstracts. A word is considered "old" if
* it isn't considered "new" (see above),
* it isn't in the list of stopwords (see `stopwords.txt`)
* it isn't present in every document (where a document is a monthly collection of abstracts) between 1970 and 2000,
* it occurs in at least 80% or 90% (matching the minimum density required by new words as described above) of the documents between 1970 and 2000,
* it contains at least one alphabet character in it.
This script outputs `old_words_0.8density.csv` or `new_words_0.9density.csv`, which is a table where rows are words and the columsn are the word itself, the number of months it appeared in, and its term frequency over the entire corpus. This script should be run on a supercomputer.

### `reformat_new_word_KLs.py`, `reformat_old_word_KLs.py`, `reformat_stopword_KLs.py`

The KL score data is currently arranged so that the dataset is cut into csv files, one for each date, and in each csv file the rows are all words occurring in that date and the columns are the word itself, KL(target, context), KL(context, target), and the symmetric KL divergence. It felt easier to me to have this data arranged into three csv files (for new words, old words, and stopwords) in which the rows are words and the columns are the word itself and then the KL scores for every date in the corpus (if KL score is missing then that cell is blank). These three scripts reformat the datasets in this manner. They output `new_word_symKL_scores_Xdensity.csv`, `old_word_symKL_scores_Xdensity.csv`, and `stop_word_symKL_scores_Xdensity.csv`.

### `get_stopword_tf.py`

Appends stopword term frequencies to the list of stopwords, outputting `stopwords.csv`.

### `graph_and_stuff.py`

This script makes a whole lot of plots for either 80% or 90% density. It also runs some OLS regressions. (It's messy; I apologize.)
