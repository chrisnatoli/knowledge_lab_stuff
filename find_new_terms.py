import csv
import os
import sys
import gc

directory = 'monthly_abstracts/'
filenames = sorted([ f for f in os.listdir(directory) ])

# Construct the following dictionary of dictionaries:
# monthly_word_counts : date --> dictionary(word --> word count for that date).
# Also construct a dictionary for total word counts:
# monthly_word_totals : date --> total number of words for that date.
dates = []
monthly_word_counts = dict()
monthly_word_totals = dict()
all_words = set()
for filename in filenames:
    gc.collect()

    date = (int(filename[ :4]), int(filename[5:-4]))
    dates.append(date)

    with open(directory+filename) as fp:
        # Read the text into a list of words.
        abstracts = fp.read()
        punctuation = (',','"',"'",'.','(',')',':')
        for p in punctuation:
            abstracts = abstracts.replace(p,'')
        words = abstracts.lower().split()

        # Construct this date's dictionary : word --> word count.
        word_counts = { word:0 for word in all_words }
        for word in words:
            if word not in all_words:
                all_words.add(word)
                for d in monthly_word_counts.keys():
                    monthly_word_counts[d][word] = 0
                word_counts[word] = 1
            else:
                word_counts[word] = word_counts[word] + 1

        monthly_word_counts[date] = word_counts
        monthly_word_totals[date] = len(words)

    print(date)

print('FINISHED READING IN DATA')

dates.sort()
all_words = sorted(list(all_words))

# Search for new words by filtering out the candidates in all_words.
start_date = (1970,1)
end_date = (2000,1)
min_freq = 50
min_density = 0.8
new_words = []
header = ['word', 'first appearance', 'term frequency', 'num months']
table = [header]
for word in all_words:
    # 1) Not seen in any preceding months
    for date in dates:
        if monthly_word_counts[date][word] > 0:
            first_appearance = date
            break
    if (first_appearance <= start_date
        or first_appearance > end_date
        or first_appearance == dates[-1]):
        continue

    '''
    # 2) A minimum frequency in the following months. I'd say 25~50
    # might be good starting place.
    raw_freq = sum([ monthly_word_counts[date][word] for date in dates
                     if date > first_appearance ])
    if raw_freq <= min_freq:
        continue
    '''

    # 3) A minimum number of following months (ie. density) in which
    # the word occurs. Maybe 10~20 would be good. Alternatively, you
    # could look for words that occur in N% of the following
    # months. Maybe 50%?
    num_months = len([ date for date in dates
                       if (date > first_appearance and
                           monthly_word_counts[date][word] > 0) ])
    total = len([ date for date in dates if date > first_appearance ])
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
