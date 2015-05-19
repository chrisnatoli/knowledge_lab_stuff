import csv
from numpy import exp, log

input_filename = 'dead_words_with_covariates.csv'
output_filename = 'dead_words_with_covariates_interpolated.csv'

data = []
with open(input_filename) as fp:
    reader = csv.reader(fp, delimiter=',')
    header = next(reader)
    for row in reader:
        interpolated_row = row[:]
        word = row[header.index('word')]
        time_origin = row[header.index('time origin')]
        end_point = row[header.index('end point')]

        for val in ['kl', 'tfidf', 'rtf']:
            time_origin_index = header.index(val + time_origin)
            end_point_index = header.index(val + end_point)

            # Linearly interpolate between each non-missing datapoint.
            not_missing = [ index for index in range(len(row))
                            if (time_origin_index <= index <= end_point_index
                                and row[index] != '') ]
            for j in range(len(not_missing)-1):
                left_index = not_missing[j]
                right_index = not_missing[j+1]
                n = right_index - left_index

                left_value = float(row[left_index])
                right_value = float(row[right_index])

                increment = (right_value - left_value) / n
                for k in range(n):
                    kth_value = left_value + k * increment
                    interpolated_row[left_index + k] = kth_value

        data.append(interpolated_row)

start_year = 1976
cutoff_year = 2005

with open(output_filename, 'w') as fp:
    writer = csv.writer(fp, delimiter=',')
    writer.writerow(['word', 'time1', 'time2', 'status', 'kl score',
                     'tfidf', 'exp.tfidf', 'log.tfidf',
                     'rtf', 'exp.rtf', 'log.rtf',
                     'time', 'age'])
    for row in data:
        for year in range(start_year, cutoff_year):
            for month in range(1,13):
                datestr = '{}-{}'.format(year, month)
                if row[header.index('kl' + datestr)] == '':
                    continue
                writer.writerow([
                    row[header.index('word')], # word
                    header.index('kl' + datestr) - 3, # time1
                    header.index('kl' + datestr) - 2, # time2
                    1 if datestr == row[header.index('end point')]
                        else 0, # status
                    row[header.index('kl' + datestr)], # kl score
                    row[header.index('tfidf' + datestr)], # tfidf
                    exp(float(row[header.index('tfidf' + datestr)])), # e^tfidf
                    log(float(row[header.index('tfidf' + datestr)])), # e^tfidf
                    row[header.index('rtf' + datestr)], # rtf
                    exp(float(row[header.index('rtf' + datestr)])), # e^rtf
                    log(float(row[header.index('rtf' + datestr)])), # e^rtf
                    header.index('kl' + datestr) - 2, # time
                    header.index('kl' + datestr) - # age
                        header.index('kl' + row[header.index('time origin')])
                    ])
