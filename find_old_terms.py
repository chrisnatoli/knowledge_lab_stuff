import csv
import os
from datetime import datetime
import multiprocessing


the_beginning = datetime.now()

directory = 'monthly_abstracts/'
corpus_filenames = sorted([ f for f in os.listdir(directory) ])
new_words_filename = 'new_words.csv'
stopwords_filename = 'stopwords.txt'
output_filename = 'old_words.txt'


# Converts '2007-7.txt' to the tuple (2007,7).
def filename_to_date(filename):
    return (int(filename[ : len('YYYY')]),
            int(filename[len('YYYY-') : -len('.txt')]))

def preprocess(text):
    text = text.lower()
    punctuation = (',','"',"'",'.','(',')',':','--','---',
                   '#','[',']','{','}','!','?','$','%',';','/')
    for p in punctuation:
        text = text.replace(p,' {} '.format(p))
    return text
    


# Read the corpus into a dictionary that maps from a date to a set
# containing all the (unique) words in that date's document.
monthly_words = dict()
for filename in corpus_filenames:
    start_time = datetime.now()

    date = filename_to_date(filename)
    with open(directory+filename) as fp:
        monthly_words[date] = set(preprocess(fp.read()).split())

    print('Text for {} was read in {}'
          .format(date, datetime.now()-start_time))

dates = sorted(monthly_words.keys())
print('The entire corpus was read in {}\n'.format(datetime.now() - the_beginning))

# Read in the new words that were previously found.
new_words = set()
with open(new_words_filename) as fp:
    reader = csv.reader(fp)
    next(reader)
    for row in reader:
        new_words.add(row[0])

# Read in a set of stop words.
stopwords = set()
with open(stopwords_filename) as fp:
    for line in fp:
        word = line.strip()
        if word != '':
            stopwords.add(word)



# Extract a list of old words. "Old words" satisfy the following:
# -- they aren't in the list of new words that were found previously,
# -- they aren't in a given list of stopwords,
# -- they aren't present in every single month in the relevant interval of time,
# -- they are in at least 90% of the documents in the relevant interval of time.
min_density = 0.9
start_date = (1970,1)#(2007,3)#
end_date = (2000,1)#(2009,1)#
relevant_dates = [ d for d in dates if start_date <= d < end_date ]

# Get a union and intersection of the relevant subset of the corpus.
all_words = set()
words_with_full_density = set(monthly_words[start_date])
for date in relevant_dates:
    words = set(monthly_words[date])
    all_words.update(words)
    words_with_full_density = words_with_full_density.intersection(words)

# Subtract out the intersection, the new words, and the stop words.
old_words = all_words.difference(words_with_full_density)
old_words = old_words.difference(new_words)
old_words = old_words.difference(stopwords)

# Assign to each remaining word the number of times it is not present in a
# month. If the number of misses exceeds the threshold defined by min_density,
# then remove this word from the set of candidates. The remaining candidates
# are considered to be the list of old words.
num_misses = { word:0 for word in old_words }
max_misses = int((1-min_density) * len(relevant_dates))
for date in relevant_dates:
    diff = old_words.difference(monthly_words[date])
    for word in diff:
        num_misses[word] += 1
    for word in old_words.copy():
        if num_misses[word] > max_misses:
            old_words.remove(word)

# Remove any words that don't have at least one alphabet
# character in them.
for word in old_words.copy():
    if not any([ char.isalpha() for char in word ]):
        old_words.remove(word)



# Dump the output into a plain text list.
old_words = sorted(list(old_words))
with open(output_filename, 'w') as fp:
    fp.write('\n'.join(old_words))

print('\nEntire script finished in '+str(datetime.now() - the_beginning))
print(old_words)
print('There are {} old words.\n'.format(len(old_words)))
