import csv
import os
import numpy as np
from datetime import datetime
import matplotlib.pylab as plt

the_beginning = datetime.now()

new_words_filename = 'new_words.csv'
kl_directory = 'medline_monthly-KL/'
new_words_header = ['word', 'first appearance', 'num months', 'term frequency']
kl_header = ['term', 'KL(tf,co)', 'KL(co,tf)', 'sym_KL_div']

# '1983-1.txt.csv' maps to (1983,1)
def kl_filename_to_date(filename):
    return (int(filename[ : len('YYYY')]),
            int(filename[len('YYYY-') : -len('.txt.csv')]))

with open(new_words_filename) as fp:
    reader = csv.reader(fp)
    next(reader)
    new_words_table = [ row for row in reader ]

kl_scores = dict()
kl_filenames = sorted([ f for f in os.listdir(kl_directory) if '.csv' in f ])
for new_word_row in new_words_table:
    new_word = new_word_row[new_words_header.index('word')]
    first_appearance = new_word_row[new_words_header.index('first appearance')]
    first_appearance = (int(first_appearance[ :-len('YYYY')]),
                        int(first_appearance[len('YYYY-'): ]))
    scores = []

    for filename in kl_filenames:
        date = kl_filename_to_date(filename)
        if date < first_appearance:
            continue
    
        with open(kl_directory+filename) as fp:
            reader = csv.reader(fp)
            for row in reader:
                if row[kl_header.index('term')] == new_word:
                    scores.append(float(row[kl_header.index('sym_KL_div')]))

        print('Found KL divergence for {} at {}'.format(new_word, date))

    kl_scores[new_word] = scores

kl_avgs = { word : np.mean(scores) for (word,scores) in kl_scores.items()
            if scores != [] }
plt.hist(list(kl_avgs.values()), bins=25)
plt.savefig('hist_of_kl_avgs.png')
plt.close()

kl_stddevs = { word : np.std(scores) for (word,scores) in kl_scores.items() 
               if scores != [] }
plt.hist(list(kl_stddevs.values()), bins=25)
plt.savefig('hist_of_kl_stddevs.png')

print('Mean of all KL scores is {}'.format(np.mean(list(kl_avgs.values()))))
print('Stddev of all KL scores is {}'.format(np.std(list(kl_avgs.values()))))
print('Entire script took {}'.format(datetime.now()-the_beginning))
