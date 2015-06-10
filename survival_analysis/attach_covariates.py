import csv
import os
from datetime import datetime



the_beginning = datetime.now()



dead_words_filename = 'dead_words_streak4_tf20.csv'
kl_directory = '../data/medline_monthly-KL/'
tf_directory = '../data/monthly_abstracts_with_tf/'
kl_suffix = '.txt.csv'
tfidf_suffix = '.txt.tfidf'
rtf_suffix = '.txt.tf.csv'



def datestr_to_date(string):
    return (int(string[: len('YYYY')]), int(string[len('YYYY-'):]))

# '1916-2.txt.csv' -> (1916, 2)
def filename_to_date(filename, suffix):
    return (int(filename[ : len('YYYY')]),
            int(filename[len('YYYY-') : -len(suffix)]))



# Read in the csv file of dead words.
dead_words_table = []
with open(dead_words_filename) as fp:
    reader = csv.reader(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    header = next(reader)
    for row in reader:
        origin = datestr_to_date(row[header.index('time origin')])
        endpoint = datestr_to_date(row[header.index('end point')])
        dead_words_table.append([row[header.index('word')],
                                 origin, endpoint])



# For each file of KL scores, look for every dead word.
# If present then record its KL score, otherwise record that it's missing.
start_year = 1976
kl_filenames = sorted([ f for f in os.listdir(kl_directory)
                        if (kl_suffix in f and
                            filename_to_date(f, kl_suffix)[0] >= start_year) ],
                      key=lambda f: filename_to_date(f, kl_suffix))

for filename in kl_filenames:
    start_time = datetime.now()

    date = filename_to_date(filename, kl_suffix)

    with open(kl_directory + filename) as fp:
        reader = csv.reader(fp, delimiter=',')
        next(reader)
        kl_rows = [ row for row in reader ]
        for dead_words_row in dead_words_table:
            #  Do not look for the word if date isn't within word's lifespan.
            if (date < dead_words_row[header.index('time origin')]
                or date > dead_words_row[header.index('end point')]):
                dead_words_row.append('')
                continue

            dead_word = dead_words_row[header.index('word')]
            for kl_row in kl_rows:
                if kl_row[0] == dead_word:
                    dead_words_row.append(kl_row[-1])
                    break
            else:
                dead_words_row.append('')

    header.append('kl{}-{}'.format(date[0], date[1]))

    print('KL scores from {} were read in {}'
          .format(date, datetime.now() - start_time))



# Since the text was preprocessed differently when finding dead words
# and when computing KL scores, some words don't have much KL score data.
# Try to omit all those words by removing dead words that have less
# than min_doc_freq points of KL data.
min_doc_freq = 12
for row in dead_words_table[:]:
    if len([ x for x in row if x != '']) < min_doc_freq + 3:
        dead_words_table.remove(row)



# Also add tfidf data to the table.
tfidf_filenames = sorted([ f for f in os.listdir(tf_directory)
                           if (tfidf_suffix in f and
                               filename_to_date(f, tfidf_suffix)[0]
                               >= start_year) ],
                         key=lambda f: filename_to_date(f, tfidf_suffix))
for filename in tfidf_filenames:
    start_time = datetime.now()
    date = filename_to_date(filename, tfidf_suffix)
    with open(tf_directory + filename) as fp:
        reader = csv.reader(fp, delimiter=',')
        word_to_tfidf = { row[1]:row[-1] for row in reader }
        for dead_words_row in dead_words_table:
            #  Do not look for the word if date isn't within word's lifespan.
            if (date < dead_words_row[header.index('time origin')]
                or date > dead_words_row[header.index('end point')]):
                dead_words_row.append('')
                continue

            dead_word = dead_words_row[header.index('word')]
            if dead_word in word_to_tfidf.keys():
                dead_words_row.append(word_to_tfidf[dead_word])
            else:
                dead_words_row.append('')

    header.append('tfidf{}-{}'.format(date[0], date[1]))

    print('TFIDFs from {} were read in {}'
          .format(date, datetime.now() - start_time))



# Also add rtf data to the table.
rtf_filenames = sorted([ f for f in os.listdir(tf_directory)
                         if (rtf_suffix in f and
                             filename_to_date(f, rtf_suffix)[0]
                             >= start_year) ],
                       key=lambda f: filename_to_date(f, rtf_suffix))
for filename in rtf_filenames:
    start_time = datetime.now()
    date = filename_to_date(filename, rtf_suffix)
    with open(tf_directory + filename) as fp:
        key_value_pairs = (fp.read().replace('{','').replace('}','')
                           .split(',')[1:])
        word_to_rtf = dict()
        for pair in key_value_pairs:
            (word, rtf) = pair.split(':')
            word_to_rtf[word.strip()[1:-1]] = rtf.strip()

        for dead_words_row in dead_words_table:
            #  Do not look for the word if date isn't within word's lifespan.
            if (date < dead_words_row[header.index('time origin')]
                or date > dead_words_row[header.index('end point')]):
                dead_words_row.append('')
                continue

            dead_word = dead_words_row[header.index('word')]
            if dead_word in word_to_rtf.keys():
                dead_words_row.append(word_to_rtf[dead_word])
            else:
                dead_words_row.append('')

    header.append('rtf{}-{}'.format(date[0], date[1]))

    print('RTFs from {} were read in {}'
          .format(date, datetime.now() - start_time))




# Convert the representation of the time origin and end point of
# each dead word from a tuple to a string.
for row in dead_words_table:
    for index in ['time origin', 'end point']:
        d = row[header.index(index)]
        row[header.index(index)] = '{}-{}'.format(d[0], d[1])



# Write to file.
output_filename = 'dead_words_with_covariates.csv'
with open(output_filename, 'w', newline='') as fp:
    writer = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    writer.writerows(dead_words_table)



print('\nEntire script finished in {}\n'
      .format(datetime.now() - the_beginning))
