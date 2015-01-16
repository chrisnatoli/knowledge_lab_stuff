import csv
import os
import numpy as np
from datetime import datetime
import matplotlib.pylab as plt

the_beginning = datetime.now()

old_words_filename = 'old_words.txt'
kl_directory = 'medline_monthly-KL/'
kl_header = ['term', 'KL(tf,co)', 'KL(co,tf)', 'sym_KL_div']

# Load in the table of old words.
with open(old_words_filename) as fp:
    old_words = [ line.strip() for line in fp ]

# Construct a dictionary from old words to a list of KL scores
# for that word over time, when available.
kl_scores = { old_word:[] for old_word in old_words }
kl_filenames = sorted([ f for f in os.listdir(kl_directory) if '.csv' in f ])
for old_word in old_words:
    scores = []

    # For each file, check if it contains a KL score for this old word.
    for filename in kl_filenames:
        with open(kl_directory+filename) as fp:
            reader = csv.reader(fp)
            next(reader)
            for row in reader:
                if row[kl_header.index('term')] == old_word:
                    scores.append(row[kl_header.index('sym_KL_div')])

        print('Found KL divergence for {} at {}'.format(old_word, filename))

    kl_scores[old_word] = scores

# Dump them all in a file.
output_filename = 'old_word_symKL_scores.txt'
with open(output_filename, 'w') as fp:
    for word in sorted(kl_scores.keys()):
        scores = ','.join(kl_scores[word])
        row = word + ',' + scores + '\n' 
        print('Writing row: {}'.format(row))
        fp.write(row)

print('Entire script took {}'.format(datetime.now()-the_beginning))
