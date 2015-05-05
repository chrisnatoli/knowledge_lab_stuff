import os
from datetime import datetime
import resource
import csv
import random


the_beginning = datetime.now()



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



start_year = 1976

directory = '/glusterfs/users/cnatoli/monthly_abstracts/'
filenames = sorted([ f for f in os.listdir(directory) ],
                     key=filename_to_date)

cutoff_year = 2005
min_streak_length = 6
min_term_freq = 40
min_doc_freq = 12
random_sample = False
print('Cutoff year is {}'.format(cutoff_year))
print('Minimum streak length = {}'.format(min_streak_length))
print('Minimum term frequency = {}'.format(min_term_freq))
print('Minimum document frequency = {}'.format(min_doc_freq))
if random_sample: print('Using a randomly selected, smaller sample')



# Read the post-1976 corpus into a dictionary that maps from a year
# to a set containing all the unique words in that year.
# Also create dictionaries from words to date of first appearance
# ("time origin") and from words to the date of last appearance ("end-point").
yearly_words = dict()
time_origins = dict()
end_points = dict()
for filename in filenames:
    start_time = datetime.now()

    date = filename_to_date(filename)

    with open(directory+filename) as fp:
        words = set(preprocess(fp.read()).split())

        # First add words to the dictionary of yearly words.
        if date[0] in yearly_words.keys():
            yearly_words[date[0]].update(words)
        else:
            yearly_words[date[0]] = words

        # Then update the time_origins and end_points dictionaries.
        for word in words:
            if word not in time_origins.keys():
                time_origins[word] = date
            end_points[word] = date

    print('Text for {} was read in {}'
          .format(date, datetime.now() - start_time))
    print('MEM: {} KB'
          .format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))

print('All text was read in {}\n'.format(datetime.now() - the_beginning))
print('MEM: {} KB'
      .format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))

years = sorted([ y for y in yearly_words.keys() if y >= start_year ])



# Accumulate a set of candidate words that occur after and including 1976.
candidates = set()
for year in years:
    candidates.update(yearly_words[year])
print('Starting with {} candidates'.format(len(candidates)))
print('MEM: {} KB'
      .format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))



# Subtract off words from years before 1976 to ensure that
# words are not left-censored.
for year in [ y for y in yearly_words.keys() if y < start_year ]:
    candidates = candidates.difference(yearly_words[year])
print('{} candidates left after selecting for new words'
      .format(len(candidates)))
print('MEM: {} KB'
      .format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))



# Find words that died (i.e., no longer occur after cutoff year)
# and that have a streak lasting at least min_streak_length years.
for candidate in candidates.copy():
    start_time = datetime.now()

    candidate_failed = False

    # First check if the candidate occured during or after the cutoff_year.
    for year in [ y for y in years if y >= cutoff_year ]:
        if candidate in yearly_words[year]:
            candidates.remove(candidate)
            candidate_failed = True
            break

    if not candidate_failed:
        # Then check if the candidate occurs in n consecutive years,
        # where n = min_streak_length.
        candidate_has_streak = False
        candidate_in_years = [ candidate in yearly_words[y] for y in years ]
        for i in range(len(candidate_in_years) - min_streak_length + 1):
            if ([True] * min_streak_length
                == candidate_in_years[i : i + min_streak_length]):
                candidate_has_streak = True
                break
        if not candidate_has_streak:
            candidates.remove(candidate)

    print('Checked candidacy of {} in {}'
          .format(candidate, datetime.now() - start_time))
    print('MEM: {} KB'
          .format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))


# Remove any candidates that don't have at least one alphabet
# character in them.
for candidate in candidates.copy():
    if not any([ char.isalpha() for char in candidate ]):
        candidates.remove(candidate)



print('{} candidates remaining'.format(len(candidates)))
print('MEM: {} KB'
      .format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))



# Take a random sample to make a toy sample of dead words
# on which to test the Cox reression model.
if random_sample:
    candidates = set(random.sample(candidates, 1000))



# Delete the yearly_words dictionary to free up memory.
for key in list(yearly_words.keys()):
    del yearly_words[key]
del yearly_words



# Check that candidates exceed a minimum term frequency
# and a minimum document frequency (where a document is a collection of
# abstracts in a give month) in post-1976 corpus.
# Simultaneously, look for words that are absent for gaps longer than
# 12 months.
infrequent_words = candidates.copy()
term_freqs = { word:0 for word in infrequent_words }
doc_freqs = { word:0 for word in infrequent_words }
gap_lengths = { word:0 for word in infrequent_words }

for filename in filenames:
    start_time = datetime.now()

    # Narrow down the set of infrequent words at every possible moment
    # to prevent computing frequencies (an expensive operation) of
    # words that are known to be sufficiently frequent.
    # If a word is not frequent enough in a given file to be removed
    # from the set of infrequent words, then add its frequencies
    # to the cumulative term_freqs and doc_freqs dictionaries.
    with open(directory+filename) as fp:
        words = preprocess(fp.read()).split()
        for infreq_word in infrequent_words.copy():
            start_time2 = datetime.now()

            tf = words.count(infreq_word)
            df = 1 if tf > 0 else 0

            # First check if minimum term frequency is exceeded.
            if tf >= min_term_freq:
                infrequent_words.remove(infreq_word)
                del term_freqs[infreq_word]
                del doc_freqs[infreq_word]
            else:
                term_freqs[infreq_word] += tf
                if term_freqs[infreq_word] >= min_term_freq:
                    infrequent_words.remove(infreq_word)
                    del term_freqs[infreq_word]
                    del doc_freqs[infreq_word]

            # If not, then check if minimum doc frequency is exceeded.
            if infreq_word in doc_freqs.keys():
                doc_freqs[infreq_word] += df
                if doc_freqs[infreq_word] >= min_doc_freq:
                    infrequent_words.remove(infreq_word)
                    del term_freqs[infreq_word]
                    del doc_freqs[infreq_word]

            print('Word frequencies of {} from {} were computed in {}'
                  .format(infreq_word, filename, datetime.now() - start_time2))
            print('MEM: {} KB'
                  .format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))

        # Separately check for words with long gap lengths and remove them
        # from future computations.
        for candidate in candidates.copy():
            if candidate in words:
                gap_lengths[candidate] = 0
            else:
                gap_lengths[candidate] += 1
            if gap_lengths[candidate] >= 12:
                candidates.remove(candidate)
                del gap_lengths[candidate]
                if candidate in infrequent_words:
                    infrequent_words.remove(candidate)
                    del term_freqs[candidate]
                    del doc_freqs[candidate]

        print('Word frequencies from {} were computed in {}'
              .format(filename, datetime.now() - start_time))
        print('MEM: {} KB'
              .format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))

# Remove the infrequent words from the list of candidates.
for infreq_word in infrequent_words:
    if term_freqs[infreq_word] < min_term_freq:
        candidates.remove(infreq_word)

print('Found {} candidates'.format(len(candidates)))



# Write the list of candidates to file with their time origins and end-points.
output_filename = 'dead_words.csv'
candidates = sorted(list(candidates))
with open(output_filename, 'w', newline='') as fp:
    writer = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['word', 'time origin', 'end point'])
    for word in candidates:
        origin_string = '{}-{}'.format(time_origins[word][0],
                                       time_origins[word][1])
        end_string = '{}-{}'.format(end_points[word][0],
                                    end_points[word][1])
        writer.writerow([word, origin_string, end_string])



print('\nEntire script finished in {}\n'
      .format(datetime.now() - the_beginning))
