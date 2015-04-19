import csv
import os
from datetime import datetime

the_beginning = datetime.now()

new_words_filename = 'new_words_0.8density.csv'
kl_directory = 'medline_monthly-KL/'
new_words_header = ['word', 'first appearance', 'num months', 'term frequency']
kl_header = ['term', 'KL(tf,co)', 'KL(co,tf)', 'sym_KL_div']

# '1983-1.txt.csv' maps to (1983,1)
def kl_filename_to_date(filename):
    return (int(filename[ : len('YYYY')]),
            int(filename[len('YYYY-') : -len('.txt.csv')]))



# Load in the table of new words.
with open(new_words_filename) as fp:
    reader = csv.reader(fp)
    next(reader)
    new_words_table = [ row for row in reader ]
new_words = [ row[new_words_header.index('word')] for row in new_words_table ]



# Construct a 2d array of new words and their KL score for every date after
# and including 1970.
kl_filenames = sorted([ f for f in os.listdir(kl_directory)
                        if '.csv' in f
                        and kl_filename_to_date(f) >= (1970,1) ])
header = ['term']
dates = sorted([ kl_filename_to_date(filename) for filename in kl_filenames ])
header.extend([ '{}-{}'.format(date[0],date[1]) for date in dates ])
kl_table = [ [new_word] + [ '' for i in range(len(dates)) ]
             for new_word in new_words ]

for new_word_row in new_words_table:
    new_word = new_word_row[new_words_header.index('word')]
    first_appearance = new_word_row[new_words_header.index('first appearance')]
    first_appearance = (int(first_appearance[ :-len('YYYY')]),
                        int(first_appearance[len('YYYY-'): ]))

    # For each file, check if it contains a KL score for this new word.
    for filename in kl_filenames:
        date = kl_filename_to_date(filename)
        if date < first_appearance:
            continue
    
        with open(kl_directory+filename) as fp:
            reader = csv.reader(fp)
            next(reader)
            for row in reader:
                if row[kl_header.index('term')] == new_word:
                    kl = row[kl_header.index('sym_KL_div')]
                    kl_table[new_words.index(new_word)][dates.index(date)+1] = kl
                    break

        print('Found KL divergence for {} at {}'.format(new_word, date))

kl_table.insert(0, header)



# Write the table to a csv file.
output_filename = 'new_word_symKL_scores_0.8density.csv'
with open(output_filename, 'w') as fp:
    for row in kl_table:
        fp.write(','.join(row) + '\n')

print('Entire script took {}'.format(datetime.now()-the_beginning))
