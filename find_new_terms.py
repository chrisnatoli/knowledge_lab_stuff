import csv
import os
import sys
import gc
import string

directory = 'monthly_abstracts/'
filenames = sorted([ f for f in os.listdir(directory) ])

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
    # 1) Not seen in any preceding months
    first_apearance = None
    for date in dates:
        if first appearance is not None:
            break
        s = ''
        for char in monthly_text[date]:
            if char in string.whitespace:
                if word == s:
                    first_apearance = date
                    break
                else:
                    s = ''
            else:
                s = s + char

    if (first_appearance <= start_date
        or first_appearance > end_date
        or first_appearance == dates[-1]):
        continue

    # 2) A minimum frequency in the following months. I'd say 25~50
    # might be good starting place.
    raw_freq = 0
    for date in dates:
        if date <= first_appearance:
            continue
        for char in monthly_date[date]:
            if char in string.whitespace:
                if word == s:
                    raw_freq = raw_freq + 1
                s = ''
            else:
                s = s + char
    '''
    if raw_freq <= min_freq:
        continue
    '''

    # 3) A minimum number of following months (ie. density) in which
    # the word occurs. Maybe 10~20 would be good. Alternatively, you
    # could look for words that occur in N% of the following
    # months. Maybe 50%?
    num_months = 0
    word_is_found = False
    for date in dates:
        if date <= first_appearance or word_is_found:
            continue
        for char in monthly_text[date]:
            if char in string.whitespace:
                if word == s:
                    word_is_found = True
                    num_months = num_months + 1
                    break
                else:
                    s = ''
            else:
                s = s + char
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
