import csv
import os
import numpy as np
from datetime import datetime


the_beginning = datetime.now()

stopwords_filename = 'stopwords.txt'
kl_directory = '../data/medline-KL_stopwords/'
kl_header = ['term', 'KL(tf,co)', 'KL(co,tf)', 'sym_KL_div']

# '1983-1.csv' maps to (1983,1)
def kl_filename_to_date(filename):
    return (int(filename[ : len('YYYY')]),
            int(filename[len('YYYY-') : -len('.csv')]))



# Load in the list of stopwords.
with open(stopwords_filename) as fp:
    stopwords = sorted([ line.strip() for line in fp if line != '\n' ])

# Construct a 2d array of stopwords and their KL score for every date after
# and including 1970.
kl_filenames = sorted([ f for f in os.listdir(kl_directory)
                        if '.csv' in f
                        and kl_filename_to_date(f) >= (1970,1) ])
header = ['term']
dates = sorted([ kl_filename_to_date(filename) for filename in kl_filenames ])
header.extend([ '{}-{}'.format(date[0],date[1]) for date in dates ])
kl_table = [ [stopword] + [ '' for i in range(len(dates)) ]
             for stopword in stopwords ]

for stopword in stopwords:
    # For each file, check if it contains a KL score for this word.
    for filename in kl_filenames:
        date = kl_filename_to_date(filename)
        with open(kl_directory+filename) as fp:
            reader = csv.reader(fp)
            next(reader)
            for row in reader:
                if row[kl_header.index('term')] == stopword:
                    kl = row[kl_header.index('sym_KL_div')]
                    kl_table[stopwords.index(stopword)][dates.index(date)+1] = kl
                    break

        print('Found KL divergence for {} at {}'.format(stopword, date))

kl_table.insert(0, header)



# Write the table to a csv file.
output_filename = 'stop_word_symKL_scores.csv'
with open(output_filename, 'w') as fp:
    for row in kl_table:
        fp.write(','.join(row) + '\n')

print('Entire script took {}'.format(datetime.now()-the_beginning))
