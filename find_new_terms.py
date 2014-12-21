import csv
import os
import sys
import gc
import string

# To conserve memory, this is a generator that effectively does the
# same job as a string's split function with whitespace as delimiter.
def split_generator(s):
    word = ''
    for char in s:
        if char in string.whitespace:
            yield word
            word = ''
        else:
            word = word + char

directory = 'monthly_abstracts/'
filenames = sorted([ f for f in os.listdir(directory) ])

# Create a dictionary mapping from the date to a string containing the
# entire text for that date. Along the way, accumulate a set of all
# the words. I chose to store the entire text in a string rather than
# in a list of words (or a dictionary from word to word frequency)
# to save memory.
dates = []
all_words = set()
monthly_text = dict()
for filename in filenames:
    #gc.collect()

    date = (int(filename[ :4]), int(filename[5:-4]))
    dates.append(date)

    with open(directory+filename) as fp:
        abstracts = fp.read()
        punctuation = (',','"',"'",'.','(',')',':')
        for p in punctuation:
            abstracts = abstracts.replace(p,'').lower()
        monthly_text[date] = abstracts

        words = abstracts.split()
        all_words.update(set(words))

    print(date)

print('FINISHED READING IN DATA')

dates.sort()
all_words = sorted(list(all_words))

# Search for new words by filtering out the candidates in all_words.
# The dates range from start_date (inclusive) to end_date (exclusive).
# When a new word is found, add it and its data to the table.
start_date = (1970,1)
end_date = (2000,1)
min_freq = 50
min_density = 0.8
header = ['word', 'first appearance', 'term frequency', 'num months']
table = [header]
for word in all_words:
    # The first filter is that a word is new if it is not seen in
    # previous months. This is implemented by finding the date of
    # first appearance and checking if that date is before the defined
    # start_date, after the end_date, and isn't the last date.
    first_appearance = None # This is just a flag to control the first forloop.
    for date in dates:
        if first_appearance is not None:
            break
        for w in split_generator(monthly_text[date]):
            if w == word:
                first_appearance = date
                break
    if (first_appearance <= start_date
        or first_appearance > end_date
        or first_appearance == dates[-1]):
        continue

    # The second filter is that a word must attain a minimum frequency
    # across the entirety of text in the following months. Trying min
    # of 25-50.
    raw_freq = 0
    for date in dates:
        if date <= first_appearance:
            continue
        for w in split_generator(monthly_text[date]):
            if w == word:
                raw_freq = raw_freq + 1
    ''' # Currently this filter is not being used.
    if raw_freq <= min_freq:
        continue
    '''

    # The third filter is that the word must occur in a minimum number
    # of months out of the following months (i.e.,
    # "density"). Shooting for densities much higher than 50%.
    num_months = 0
    for date in dates:
        if date <= first_appearance:
            continue
        for w in split_generator(monthly_text[date]):
            if w == word:
                num_months = num_months + 1
                break
    total = len(dates) - dates.index(first_appearance) - 1
    density = num_months / total
    if density <= min_density:
        continue

    # If the word passes the filters, then add it to the table.
    # The header of the table is as follows: word, date of first
    # appearance, raw term frequency after first appearance, number of
    # months it occurs in after the first appearance.
    table.append([ word, '{}-{}'.format(date[0],date[1]),
                   raw_freq, num_months ])

# Compose the printout for testing:
new_words = [ row[0] for row in table[1: ] ]
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
