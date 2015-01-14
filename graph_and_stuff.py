import csv
import numpy as np
import matplotlib.pylab as plt



KLs_filename = '_word_symKL_scores.txt'

# For both old and new words, plot three histograms:
# - one of all KL scores for all new words,
# - one of the mean KL score for each new word, and
# - another of stddev of the KL scores for each new word.
#oldnew = ('old','new')
oldnew = ['new']
kl_scores = dict()
flat_kl_scores = dict()
kl_means = dict()
kl_stddevs = dict()
for when in oldnew:
    kl_scores[when] = dict()
    with open(when + KLs_filename) as fp:
        for line in fp:
            tokens = line.strip().split(',')
            word = tokens[0]
            if tokens[1] == '':
                continue
            scores = list(map(float, tokens[1:]))
            if scores != []:
                kl_scores[when][word] = scores
    
    flat_kl_scores[when] = []
    for word in kl_scores[when].keys():
        flat_kl_scores[when].extend(kl_scores[when][word])
    plt.hist(flat_kl_scores[when], bins=50)
    plt.savefig('plots/hist_of_{}_symKL_scores.png'.format(when))
    plt.close()
    
    kl_means[when] = { word : np.mean(scores) for (word,scores)
                      in kl_scores[when].items() }
    plt.hist(list(kl_means[when].values()), bins=50)
    plt.savefig('plots/hist_of_{}_symKL_means.png'.format(when))
    plt.close()
    
    kl_stddevs[when] = { word : np.std(scores) for (word,scores)
                         in kl_scores[when].items() }
    plt.hist(list(kl_stddevs[when].values()), bins=50)
    plt.savefig('plots/hist_of_{}_symKL_stddevs.png'.format(when))
    plt.close()



# Make a single scatterplot of tuples (mean, stddev) for
# both old and new word.
for when in oldnew:
    xs = [ kl_means[when][word] for word in kl_scores[when].keys() ]
    ys = [ kl_stddevs[when][word] for word in kl_scores[when].keys() ]
    c = 'green' if when == 'old' else 'blue'
    plt.scatter(xs, ys, s=1, color=c)
plt.xlabel('Mean KL score of a given word over time')
plt.ylabel('Standard deviation of KL scores for a given word over time')
plt.savefig('plots/scatter_symKL_mean_vs_std_old_and_new.png')
plt.close()



# Make another scatterplot of tuples 9mean, stddev) for only new
# words, where the point is colored by the year of the word's
# first appearance.
def string_to_date(date):
    return (int(date[ : len('YYYY')]), int(date[len('YYYY-') : ]))
    
new_words_filename = 'new_words.csv'
with open(new_words_filename) as fp:
    reader = csv.reader(fp, delimiter=',')
    header = next(reader)
    table = [ row for row in csv.reader(fp, delimiter=',') ]

first_appearances = { row[header.index('word')] :
                        string_to_date(row[header.index('first appearance')])
                      for row in table }

xs = [ kl_means['new'][word] for word in kl_scores['new'].keys() ]
ys = [ kl_stddevs['new'][word] for word in kl_scores['new'].keys() ]
cs = [ plt.cm.coolwarm((first_appearances[word][0]-1970)/(2000-1970))
       for word in kl_scores['new'].keys() ]
plt.scatter(xs, ys, s=1, color=cs)
plt.xlabel('Mean KL score of a given word over time')
plt.ylabel('Standard deviation of KL scores for a given word over time')
plt.savefig('plots/scatter_symKL_mean_vs_std_with_yr.png')
plt.close()






# And then do some other stuff:

# Dump the scores, means, and stddevs for new words into plaintext files so
# they'll be easy to read into R.
output_directory = 'tmp/'
output_filenames = ['all_KLs','all_KL_means','all_KL_stddevs']
output_data = [flat_kl_scores['new'],
               kl_means['new'].values(),
               kl_stddevs['new'].values() ]
for i,filename in enumerate(output_filenames):
    with open(output_directory + filename, 'w') as fp:
        fp.write('\n'.join([ str(x) for x in output_data[i] ]))

# Use a normal distribution to sample words from the two peaks of the
# bimodal distribution of new words.
kl_means = sorted([ (avg,word) for (word,avg) in kl_means['new'].items() ])
left_peak = 1.9
right_peak = 2.1
stddev = 0.03
num_samples = 400
left_words = set()
right_words = set()

for peak in (left_peak, right_peak):
    for i in range(num_samples):
        r = np.random.randn() * stddev + peak
        for (avg,word) in kl_means:
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
