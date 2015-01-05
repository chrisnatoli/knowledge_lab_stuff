import csv
import numpy as np
import matplotlib.pylab as plt


# Plot a bar graph of the number of new words each year.

input_filename = 'new_words.csv'

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
plt.close()



# Plot three histograms:
# - one of all KL scores for all new words,
# - one of the mean KL score for each new word, and
# - another of stddev of the KL scores for each new word.
# Also make a scatterplot of tuples (mean, stddev) for each word.
input_filename = 'new_word_KL_scores.txt'
kl_scores = dict()
with open(input_filename) as fp:
    for line in fp:
        tokens = line.strip().split(',')
        word = tokens[0]
        if tokens[1] == '':
            continue
        scores = list(map(float, tokens[1:]))
        kl_scores[word] = scores

kls = []
for word in kl_scores.keys():
    kls.extend(kl_scores[word])
plt.hist(kls, bins=25)
plt.savefig('hist_of_kl_scores.png')
plt.close()

kl_avgs = { word : np.mean(scores) for (word,scores) in kl_scores.items()
            if scores != [] }
plt.hist(list(kl_avgs.values()), bins=25)
plt.savefig('hist_of_kl_avgs.png')
plt.close()

kl_stddevs = { word : np.std(scores) for (word,scores) in kl_scores.items() 
               if scores != [] }
plt.hist(list(kl_stddevs.values()), bins=25)
plt.savefig('hist_of_kl_stddevs.png')
plt.close()

xs = [ kl_avgs[word] for word in kl_scores.keys() if kl_scores[word] != [] ]
ys = [ kl_stddevs[word] for word in kl_scores.keys() if kl_scores[word] != [] ]
plt.scatter(xs,ys,s=1)
plt.xlabel('Mean KL score of a given word over time')
plt.ylabel('Standard deviation of KL scores for a given word over time')
plt.savefig('scatter_kl_mean_vs_std.png')
plt.close()
