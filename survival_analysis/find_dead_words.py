import os
from datetime import datetime
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

directory = 'monthly_abstracts/'
filenames = sorted([ f for f in os.listdir(directory) ])


# Read the post-1976 corpus into a dictionary that maps from a year
# to a set containing all the unique words in that year.
yearly_words = dict()
for filename in filenames:
    start_time = datetime.now()

    date = filename_to_date(filename)

    with open(directory+filename) as fp:
        words = set(preprocess(fp.read()).split())
        if date[0] in yearly_words.keys():
            yearly_words[date[0]].update(words)
        else:
            yearly_words[date[0]] = words

    print('Text for {} was read in {}'
          .format(date, datetime.now() - start_time))

print('All text was read in {}\n'.format(datetime.now() - the_beginning))

years = sorted([ y for y in yearly_words.keys() if y >= start_year ])


# Accumulate a set of candidate words that occur after and including 1976.
candidates = set()
for year in years:
    candidates.update(yearly_words[year])
print('Starting with {} candidates'.format(len(candidates)))


# Subtract off words from years before 1976 to ensure that
# words are not left-censored.
for year in [ y for y in yearly_words.keys() if y < start_year ]:
    candidates.subtract(yearly_words[year])
print('{} candidates left after selecting for new words'
      .format(len(candidates)))



# Find words that died (i.e., no longer occur after cutoff year)
# and that satisfy certain constraints to confirm their relevancy.
cutoff_year = 2005
min_streak_length = 5

for candidate in candidates.copy():
    start_time = datetime.now()

    candidate_failed = False

    # First check if the candidate occured after the cutoff_year.
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



# Remove any candidates that don't have at least one alphabet
# character in them.
for candidate in candidates.copy():
    if not any([ char.isalpha() for char in candidate ]):
        candidates.remove(candidate)



print('{} candidates remaining'.format(len(candidates)))



# Also check that candidates exceed a minimum term frequency
# in post-1976 corpus.
min_term_freq = 10
infrequent_words = candidates.copy()
term_freqs = { word:0 for word in infrequent_words }

for filename in filenames:
    start_time = datetime.now()

    # Narrow down the set of infrequent words at every possible moment
    # to prevent computing frequencies (an expensive operation) of
    # words that are known to be sufficiently frequent.
    # If a word is not frequent enough in a given file to be removed
    # from the set of infrequent words, then add its word frequency
    # to the cumulative term_freqs dictionary.
    with open(directory+filename) as fp:
        words = preprocess(fp.read()).split()
        for infreq_word in infrequent_words.copy():
            start_time2 = datetime.now()

            count = words.count(infreq_word)
            if count >= min_term_freq:
                infrequent_words.remove(infreq_word)
                del term_freqs[infreq_word]
            else:
                term_freqs[infreq_word] += count
                if term_freqs[infreq_word] >= min_term_freq:
                    infrequent_words.remove(infreq_word)
                    del term_freqs[infreq_word]

            print('Word frequency of {} from {} was computed in {}'
                  .format(infreq_word, filename, datetime.now() - start_time))

    print('Word frequencies from {} were computed in {}'
          .format(filename, datetime.now() - start_time))

# Remove the infrequent words from the list of candidates.
for infreq_word in infrequent_words:
    if term_freqs[infreq_word] < min_term_freq:
        candidates.remove(infreq_word)

print('\nEntire script finished in {}\n'
      .format(datetime.now() - the_beginning))

print(candidates)
print(len(candidates))
