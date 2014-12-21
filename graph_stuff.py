import csv
import numpy as np
import matplotlib.pylab as plt

input_filename = 'new_words_10.csv'

def string_to_date(date):
    return (int(date[ : len('YYYY')]), int(date[len('YYYY-') : ]))


with open(input_filename) as fp:
    table = [ row for row in csv.reader(fp, delimiter=',') ]

dates = sorted([ (year, month) for year in range(1970,2000)
                 for month in range(1,13) ])
first_appearances = [ string_to_date(row[1]) for row in table[1:] ]
word_counts = [ first_appearances.count(date) for date in dates ]

rang = range(0,len(dates),12)
ticks = [ '{}-{}'.format(dates[i][0], dates[i][1]) for i in rang ]

plt.bar(range(len(dates)), word_counts)
plt.xticks(rang, ticks, rotation='vertical')
plt.savefig('new_words_per_year.png', dpi=300)
