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
input_filename = 'new_word_KLcotf_scores.txt'
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
plt.hist(kls, bins=50)
plt.savefig('plots/hist_of_KLcotf_scores.png')
plt.close()

kl_avgs = { word : np.mean(scores) for (word,scores) in kl_scores.items()
            if scores != [] }
plt.hist(list(kl_avgs.values()), bins=50)
plt.savefig('plots/hist_of_KLcotf_avgs.png')
plt.close()

kl_stddevs = { word : np.std(scores) for (word,scores) in kl_scores.items() 
               if scores != [] }
plt.hist(list(kl_stddevs.values()), bins=50)
plt.savefig('plots/hist_of_KLcotf_stddevs.png')
plt.close()

xs = [ kl_avgs[word] for word in kl_scores.keys() if kl_scores[word] != [] ]
ys = [ kl_stddevs[word] for word in kl_scores.keys() if kl_scores[word] != [] ]
plt.scatter(xs,ys,s=1)
plt.xlabel('Mean KL score of a given word over time')
plt.ylabel('Standard deviation of KL scores for a given word over time')
plt.savefig('plots/scatter_KLcotf_mean_vs_std.png')
plt.close()



# And then do some other stuff:

# Dump the scores, means, and stddevs into plaintext files so
# they'll be easy to read into R.
output_directory = 'tmp/'
output_filenames = ['all_KLs','all_KL_means','all_KL_stddevs']
output_data = [kls, kl_avgs.values(), kl_stddevs.values() ]
for i,filename in enumerate(output_filenames):
    with open(output_directory + filename, 'w') as fp:
        fp.write('\n'.join([ str(x) for x in output_data[i] ]))

# Use a normal distribution to sample words from the two peaks of the
# bimodal distribution of words.
kl_avgs = sorted([ (avg,word) for (word,avg) in kl_avgs.items() ])
left_peak = 1.7
right_peak = 1.9
stddev = 0.3
num_samples = 200
left_words = set()
right_words = set()

for peak in (left_peak, right_peak):
    for i in range(num_samples):
        r = np.random.randn() * stddev + peak
        for (avg,word) in kl_avgs:
            if avg > r:
                if peak == left_peak:
                    left_words.add(word)
                else:
                    right_words.add(word)
                break
left_filename = 'left_peak.txt'
with open(left_filename, 'w') as fp:
    fp.write('\n'.join(sorted(list(left_words))))
right_filename = 'right_peak.txt'
with open(right_filename, 'w') as fp:
    fp.write('\n'.join(sorted(list(right_words))))
