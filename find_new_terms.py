import csv
import os
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

directory = 'monthly_abstracts/'
filenames = sorted([ f for f in os.listdir(directory) ])
fullpaths = [ directory+f for f in filenames ]
dates = sorted([ (int(filename[ : len('YYYY')]),
                  int(filename[len('YYYY-') : -len('.txt')]))
                 for filename in filenames ])

def preprocess(text):
    text = text.lower()
    punctuation = (',','"',"'",'.','(',')',':','--','---',
                   '#','[',']','{','}','!','?','$','%',';')
    for p in punctuation:
        text = text.replace(p,' {} '.format(p))
    return text

def tokenize(text):
    return text.split()

vectorizer = CountVectorizer(input='filename',
                             preprocessor=preprocess,
                             tokenizer=tokenize)
counts = vectorizer.fit_transform(fullpaths).toarray()
all_words = vectorizer.get_feature_names()

print('CORPUS IS VECTORIZED')

start_date = (1970,1)
end_date = (2100,1)
min_freq = 50
min_density = 0.8
header = ['word', 'first appearance', 'term freqency', 'num months']
table = [header]
# For every word in the corpus, check that it passes a few filters in
# order to be considered a new word. If it does, add it to the table
# along with some information about it.
for word in all_words:
    print(word)

    # First filter:
    # Word does not appear before start_date.
    for date in dates:
        if counts[dates.index(date)][all_words.index(word)] != 0:
            first_appearance = date
            break
    if (first_appearance <= start_date
        or first_appearance > end_date
        or first_appearance == dates[-1]):
        continue

    # Second filter:
    # Word occurs at least min_freq times after its first appearance.
    raw_freq = sum([ counts[dates.index(date)][all_words.index(word)]
                     for date in dates if date > first_appearance ])
    #if raw_freq <= min_freq:
    #    continue

    # Third filter:
    # Word occurs in at least x% of the months following its first
    # appearance, where x% = min_density.
    num_months = len([ date for date in dates
                       if (date > first_appearance and
                           counts[dates.index(date)][all_words.index(word)] > 0) ])
    total = len(dates) - dates.index(first_appearance) - 1
    density = num_months / total
    if density <= min_density:
        continue
    
    # If the word passes all the filters, then add it to the table.
    # The header of the table is as follows: word, date of first
    # appearance, raw term frequency after first appearance, number of
    # months it occurs in after the first appearance.
    table.append([ word, '{}-{}'.format(date[0],date[1]),
                   raw_freq, num_months ])


# Compose the printout for testing:
new_words = [ row[0] for row in table ]
printout = '''min_density = {}
start_date = {}
end_date = {}

number of new words = {}

new words:
{}
'''.format(min_density, start_date, end_date,
           len(new_words), ' '.join(new_words))
print(printout)

output_filename = 'new_words.csv'
with open(output_filename, 'w', newline='') as fp:
    writer = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(table)
