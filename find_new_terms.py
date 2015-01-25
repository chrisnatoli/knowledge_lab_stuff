import csv
import os
from datetime import datetime
import multiprocessing


the_beginning = datetime.now()

directory = 'monthly_abstracts/'
filenames = sorted([ f for f in os.listdir(directory) ])


def partition(liszt, num_parts):
    return [ [ liszt[i] for i in range(len(liszt)) 
               if i % num_parts == j ]
             for j in range(num_parts) ]

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
for filename in filenames:
    start_time = datetime.now()

    date = filename_to_date(filename)
    with open(directory+filename) as fp:
        monthly_words[date] = set(preprocess(fp.read()).split())

    print('Text for {} was read in {}'
          .format(date, datetime.now()-start_time))

dates = sorted(monthly_words.keys())

print('All text was read in {}\n'.format(datetime.now() - the_beginning))



# Find new words using multiple processes.
num_processes = 4
stdout_lock = multiprocessing.Lock()
manager = multiprocessing.Manager()
min_density = 0.9
start_date = (1970,1)#(2007,3)#
end_date = (2000,1)#(2009,1)#
relevant_dates = [ d for d in dates if start_date <= d < end_date ]
new_words = manager.list()

# For each date in the given list of dates, consider the date's text
# as a set of candidate new words. Subtract from this set all words in
# previous months. Then assign to each remaining word the number of
# times it is not present in following months. If the number of misses
# exceeds the threshold defined by min_density, then remove this word
# from the set of candidates. Any remaining candidates are added to
# the list of new words.
def find_new_terms_in_dates(sublist):
    for date in sublist:
        start_time = datetime.now()

        candidates = monthly_words[date].copy()

        # Subtract from the candidates all words in previous months, to
        # ensure that the candidates are new.
        for past_date in [ d for d in dates if d < date ]:
            candidates = candidates.difference(monthly_words[past_date])
        if not candidates:
            with stdout_lock:
                print('No candidates from {} left after subtraction with'
                      +' previous months.'.format(date))
                print('This loop took {}.\n'
                      .format(date, datetime.now() - start_time))
            continue

        # Rather than intersect the candidates with /every/ following
        # month, consider the candidates that are in some but not all of
        # the following months. If a candidate misses too many months (as
        # defined by min_density), then it loses candidacy. Any that
        # remain after comparing with every following month are considered
        # relevant enough to the literature to be new words.
        num_misses = { word:0 for word in candidates }
        max_misses = int((1-min_density) * len([ d for d in dates if d>date ]))
        for future_date in [ d for d in dates if d > date ]:
            diff = candidates.difference(monthly_words[future_date])
            for word in diff:
                num_misses[word] += 1
            for word in candidates.copy():
                if num_misses[word] > max_misses:
                    candidates.remove(word)

            if not candidates:
                with stdout_lock:
                    print('No candidates from {} left after comparing with {}'
                          .format(date, future_date))
                    print('This loop took {}.\n'
                          .format(datetime.now() - start_time))
                break

        # If there are any candidates left, add them to new_words.
        else:
            with stdout_lock:
                print('Adding the following words from {} to new_words:'
                      .format(date))
                print(candidates)
                print('This loop took {}.\n'
                      .format(datetime.now() - start_time))

            new_words.extend(candidates)

# Partition the list of dates into n sublists, where n=num_processes.
# Give each process a single part of the partition.
dates_partition = partition(relevant_dates, num_processes)
pool = multiprocessing.Pool(processes=num_processes)
pool.map(find_new_terms_in_dates, dates_partition)
pool.close()
pool.join()
        
# Remove any words that don't have at least one alphabet
# character in them.
for word in new_words[:]:
    if not any([ char.isalpha() for char in word ]):
        new_words.remove(word)
    if 'year-old' in word:
        new_words.remove(word)

new_words.sort()
print('\nFinished finding new words in {}'
      .format(datetime.now() - the_beginning))
print(new_words)
print('There are {} new words.\n'.format(len(new_words)))



# After finding all the new words, get some data about them: their
# first appearance, the number of months they appear in, and their
# term frequency in the entire corpus.
header = ['word', 'first appearance', 'num months', 'term frequency']
table = []

# Find the word's first appearance and the number of months
# it appears in by using the monthly sets of words.
for word in new_words:
    start_time = datetime.now()

    first_appearance = None
    num_months = 0
    for date in dates:
        if word in monthly_words[date]:
            if first_appearance is None:
                first_appearance = date
            num_months += 1

    table.append([word, first_appearance, num_months])

    print('Data about "{}" was computed in {}'
          .format(word, datetime.now()-start_time))

# Delete the monthly_words dictionary to free up memory
# to read in the corpus as strings.
for key in list(monthly_words.keys()):
    del monthly_words[key]
del monthly_words

# It is no longer possible to read the entire corpus into memory, so
# instead partition the corpus and read only parts in at a time.
# Then compute the word frequencies within those parts.
filenames_partition = partition([ f for f in filenames
                                  if filename_to_date(f) >= start_date ],
                                3)
word_frequencies = { word:0 for word in new_words }

for sublist in filenames_partition:
    start_time = datetime.now()

    # Read in all the text for those dates in the sublist.
    monthly_text = dict()
    for filename in sublist:
        start_time2 = datetime.now()

        date = filename_to_date(filename)
        with open(directory+filename) as fp:
            monthly_text[date] = preprocess(fp.read())

        print('Text for {} was read (again) in {}'
              .format(date, datetime.now()-start_time2))

    print('Sublist was read in {}\n'.format(datetime.now()-start_time))
    start_time = datetime.now()

    # From this new dictionary, compute the frequency of every new word
    # across the entire corpus. Although this feels like a roundabout way
    # of doing this, it seems to be the only way that's moderately fast
    # and doesn't run out of memory.
    for row in table:
        start_time2 = datetime.now()
        word = row[header.index('word')]
        first_appearance = row[header.index('first appearance')]

        frequency = 0
        dates_sublist = [ filename_to_date(f) for f in sublist ]
        for date in [ d for d in dates_sublist if d >= first_appearance ]:
            frequency += monthly_text[date].count(word)
        word_frequencies[word] += frequency

        print('Frequency of "{}" in this sublist was computed in {}'
              .format(word, datetime.now()-start_time2))

    del monthly_text

    print('Frequencies for this sublist were computed in {}\n'
          .format(datetime.now()-start_time))
    

# Fix up the table to prepare for output.
for row in table:
    word = row[header.index('word')]
    row.append(word_frequencies[word])

    date = row[header.index('first appearance')]
    row[header.index('first appearance')] = '{}-{}'.format(date[0],date[1])
table.sort()
table.insert(0, header)

output_filename = 'new_words.csv'
with open(output_filename, 'w', newline='') as fp:
    writer = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(table)

print('\nEntire script finished in '+str(datetime.now() - the_beginning))
