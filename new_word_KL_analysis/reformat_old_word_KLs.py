import csv
import os
import numpy as np
from datetime import datetime


the_beginning = datetime.now()

old_words_filename = 'old_words_0.8density.csv'
kl_directory = 'medline_monthly-KL/'
kl_header = ['term', 'KL(tf,co)', 'KL(co,tf)', 'sym_KL_div']

# '1983-1.txt.csv' maps to (1983,1)
def kl_filename_to_date(filename):
    return (int(filename[ : len('YYYY')]),
            int(filename[len('YYYY-') : -len('.txt.csv')]))



# Load in the list of old words.
with open(old_words_filename) as fp:
    reader = csv.reader(fp)
    next(reader)
    old_words = [ row[0] for row in reader ]

# Construct a 2d array of old words and their KL score for every date after
# and including 1970.
kl_filenames = sorted([ f for f in os.listdir(kl_directory)
                        if '.csv' in f
                        and kl_filename_to_date(f) >= (1970,1) ])
header = ['term']
dates = sorted([ kl_filename_to_date(filename) for filename in kl_filenames ])
header.extend([ '{}-{}'.format(date[0],date[1]) for date in dates ])
kl_table = [ [old_word] + [ '' for i in range(len(dates)) ]
             for old_word in old_words ]

for old_word in old_words:
    # For each file, check if it contains a KL score for this word.
    for filename in kl_filenames:
        date = kl_filename_to_date(filename)
        with open(kl_directory+filename) as fp:
            reader = csv.reader(fp)
            next(reader)
            for row in reader:
                if row[kl_header.index('term')] == old_word:
                    kl = row[kl_header.index('sym_KL_div')]
                    kl_table[old_words.index(old_word)][dates.index(date)+1] = kl
                    break

        print('Found KL divergence for {} at {}'.format(old_word, date))

kl_table.insert(0, header)



# Write the table to a csv file.
output_filename = 'old_word_symKL_scores_0.8density.csv'
with open(output_filename, 'w') as fp:
    for row in kl_table:
        fp.write(','.join(row) + '\n')

print('Entire script took {}'.format(datetime.now()-the_beginning))
