import csv
import os
from datetime import datetime

the_beginning = datetime.now()

directory = 'monthly_abstracts/'
filenames = sorted([ f for f in os.listdir(directory) ])

# Read the corpus into a dictionary from dates to a string containing
# that date's text.
monthly_text = dict()
for filename in filenames:
    start_time = datetime.now()

    date = (int(filename[ : len('YYYY')]),
            int(filename[len('YYYY-') : -len('.txt')]))

    with open(directory+filename) as fp:
        text = fp.read().lower()
        punctuation = (',','"',"'",'.','(',')',':','--','---',
                       '#','[',']','{','}','!','?','$','%',';')
        for p in punctuation:
            text = text.replace(p,' {} '.format(p))
        monthly_text[date] = set(text.split())

    print('Text for {} was read in {}'.format(str(date),
                                              str(datetime.now()-start_time)))

dates = sorted(monthly_text.keys())

print('All text was read in ' + str(datetime.now() - the_beginning))

exit()

# Consider each month's text as a set of candidate new words. Subtract
# from this set all words in previous months. Intersect the remainder
# with all future months.
min_density = 0.9
start_date = (1970,1)#(2007,3)#
end_date = (2000,1)#(2009,1)#
new_words = set()
for date in [ d for d in dates if start_date <= d < end_date ]:
    print('\nConsidering the candidate set of words from '+str(date))
    start_time = datetime.now()

    candidates = set(monthly_text[date].split())

    # Subtract from the candidates all words in previous months, to
    # ensure that the candidates are new.
    for past_date in [ d for d in dates if d < date ]:
        candidates = candidates.difference(
            set(monthly_text[past_date].split()))
    if not candidates:
        print('No candidates left after subtraction with previous months.')
        print('This loop took '+str(datetime.now() - start_time))
        continue

    # Rather than intersect the candidates with /every/ following
    # month, consider the candidates that are in some but not all of
    # the following months. If a candidate misses too many months (as
    # defined by min_density), then it loses candidacy. Any that
    # remain after comparing with every following month are considered
    # relevant enough to the literature to be new words.
    num_misses = { word:0 for word in candidates }
    max_misses = int((1-min_density) * len([ d for d in dates if d > date ]))
    for future_date in [ d for d in dates if d > date ]:
        diff = candidates.difference(set(monthly_text[future_date].split()))
        for word in diff:
            num_misses[word] = num_misses[word] + 1
        for word in candidates.copy():
            if num_misses[word] > max_misses:
                candidates.remove(word)
        if not candidates:
            print('No candidates left after comparing with {}'.format(
                    future_date))
            print('This loop took '+str(datetime.now() - start_time))
            break
    else:
        # If there are any candidates left, add them to new_words.
        print('Updating new words with the following:\n{}'.format(
                candidates))
        print('This loop took '+str(datetime.now() - start_time))
        new_words.update(candidates)
        
print('\nEntire script complete in '+str(datetime.now() - the_beginning))
print(new_words)
print(len(new_words))
