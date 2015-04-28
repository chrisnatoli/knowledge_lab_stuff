import csv
import os
from datetime import datetime



the_beginning = datetime.now()



dead_words_filename = 'dead_words_streak6_tf40.csv'
kl_directory = '../data/medline_monthly-KL/'



def datestr_to_date(string):
    string = string[1:-1]
    return (int(string[:4]), int(string[6:]))

def filename_to_date(filename):
    return (int(filename[ : len('YYYY')]),
            int(filename[len('YYYY-') : -len('.txt.csv')]))



# Read in the csv file of dead words.
dead_words_table = []
with open(dead_words_filename) as fp:
    reader = csv.reader(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    header = next(reader)
    for row in reader:
        origin = datestr_to_date(row[header.index('time origin')])
        endpoint = datestr_to_date(row[header.index('end point')])
        dead_words_table.append([row[header.index('word')],
                                '{}-{}'.format(origin[0], origin[1]),
                                '{}-{}'.format(endpoint[0], endpoint[1])])



# For each file of KL scores, look for every dead word.
# If present then record its KL score, otherwise record that it's missing.
start_year = 1976
kl_filenames = sorted([ f for f in os.listdir(kl_directory)
                        if ('.txt.csv' in f
                            and filename_to_date(f)[0] >= start_year) ])

for filename in kl_filenames:
    start_time = datetime.now()

    with open(kl_directory + filename) as fp:
        reader = csv.reader(fp, delimiter=',')
        next(reader)
        kl_rows = [ row for row in reader ]
        for dead_words_row in dead_words_table:
            # (NOTE: Make this more efficient: do not look for 
            #  dead words if the date is not within the word's lifespan.)
            dead_word = dead_words_row[header.index('word')]
            for kl_row in kl_rows:
                if kl_row[0] == dead_word:
                    dead_words_row.append(kl_row[-1])
                    break
            else:
                dead_words_row.append('')

    date = filename_to_date(filename)
    header.append('{}-{}'.format(date[0], date[1]))

    print('KL scores from {} were read in {}'
          .format(date, datetime.now() - start_time))



# Since the text was preprocessed differently when finding dead words
# and when computing KL scores, some words don't have much KL score data.
# Try to omit all those words by removing dead words that have less
# than min_streak_length points of KL data.
# (NOTE: this should be fixed for production use.)
min_streak_length = 6
for row in dead_words_table[:]:
    if len([ x for x in row if x != '']) < min_streak_length + 3:
        dead_words_table.remove(row)




# Write to file.
output_filename = 'dead_words_with_kl.csv'
with open(output_filename, 'w', newline='') as fp:
    writer = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    writer.writerows(dead_words_table)



print('\nEntire script finished in {}\n'
      .format(datetime.now() - the_beginning))
