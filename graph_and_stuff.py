import csv
import numpy as np
import matplotlib.pylab as plt



def string_to_date(s):
    return (int(s[ : len('YYYY')]), int(s[len('YYYY-') : ]))
    
def remove_nones(xs):
    return [ x for x in xs if x is not None ]



kls_filename = '_word_symKL_scores.csv'

# For both old and new words, plot three histograms:
# - one of all KL scores for all words,
# - one of the mean KL score for each word, and
# - another of stddev of the KL scores for each word.
oldnew = ('old','new')
words = dict()
kl_scores = dict()
flat_kl_scores = dict()
kl_means = dict()
kl_stddevs = dict()
for when in oldnew:
    # Load the data into a dictionary from words to lists of scores.
    kl_scores[when] = dict()
    words[when] = []
    with open(when + kls_filename) as fp:
        dates = [ string_to_date(s) for s in
                  fp.readline().strip().split(',')[1:] ]
        for line in fp:
            tokens = line.strip().split(',')
            word = tokens[0]
            scores = [ float(score) if score != '' else None
                       for score in tokens[1:] ]
            kl_scores[when][word] = scores
            words[when].append(word)
    
    # Generate lists of KL scores, ignoring empty datapoints and
    # words that lack KL scores.
    flat_kl_scores[when] = []
    kl_means[when] = []
    kl_stddevs[when] = []
    for word in words[when]:
        scores = remove_nones(kl_scores[when][word])
        if scores != []:
            flat_kl_scores[when].extend(scores)
            kl_means[when].append(np.mean(scores))
            kl_stddevs[when].append(np.std(scores))

    # Plot a histogram of all KL scores.
    plt.hist(flat_kl_scores[when], bins=50)
    plt.savefig('plots/hist_of_{}_symKL_scores.png'.format(when))
    plt.close()
    
    # Plot a histogram of the mean KL score for each word, collapsing
    # a word's KL scores over time.
    plt.hist(kl_means[when], bins=50)
    plt.savefig('plots/hist_of_{}_symKL_means.png'.format(when))
    plt.close()
    
    # Plot a histogram of the stddev of KL scores for each word, collapsing
    # a word's KL scores over time.
    plt.hist(kl_stddevs[when], bins=50)
    plt.savefig('plots/hist_of_{}_symKL_stddevs.png'.format(when))
    plt.close()



# Make a single scatterplot of tuples (mean, stddev) for
# both old and new word.
for when in oldnew:
    plt.scatter(kl_means[when], kl_stddevs[when], s=1,
                color='green' if when == 'old' else 'blue')
plt.xlabel('Mean KL score of a given word over time')
plt.ylabel('Standard deviation of KL scores for a given word over time')
plt.savefig('plots/scatter_symKL_mean_vs_std_old_and_new.png')
plt.close()



# Make a scatterplot of tuples (mean, stddev) for only new
# words, where the point is colored by the time of the word's
# first appearance.
new_words_filename = 'new_words.csv'
with open(new_words_filename) as fp:
    reader = csv.reader(fp, delimiter=',')
    header = next(reader)
    table = sorted([ row for row in csv.reader(fp, delimiter=',') ])
first_appearances = { row[header.index('word')]
                      : string_to_date(row[header.index('first appearance')])
                      for row in table }
colors = [ plt.cm.coolwarm((first_appearances[word][0]-1970)/(2000-1970))
           for word in words['new']
           if remove_nones(kl_scores['new'][word]) != [] ]

fig, ax = plt.subplots()
ax.set_axis_bgcolor('0.25')
ax.scatter(kl_means['new'], kl_stddevs['new'], s=1, color=colors)
plt.xlabel('Mean KL score of a given word over time')
plt.ylabel('Standard deviation of KL scores for a given word over time')
plt.savefig('plots/scatter_symKL_mean_vs_std_with_yr.png')
plt.close()



# More scatterplots: mean vs date of first appearance and stddev vs date.
firsts = [ first_appearances[word][0] + float(first_appearances[word][1]-1)/12
           for word in words['new']
           if remove_nones(kl_scores['new'][word]) != [] ]
plt.scatter(firsts, kl_means['new'], s=1)
plt.xlabel('Date of first appearance')
plt.ylabel('Mean KL score of a given word over time')
plt.savefig('plots/scatter_mean_KL_vs_first_appearance.png')
plt.close()

plt.scatter(firsts, kl_stddevs['new'], s=1)
plt.xlabel('Date of first appearance')
plt.ylabel('Standard deviation of KL scores of a given word over time')
plt.savefig('plots/scatter_stddev_KL_vs_first_appearance.png')
plt.close()



# Rather than look at mean and stddev of a word over the entire duration of the
# word's time series, just look at the next n years. Check
# out the colored scatterplot and the histograms of means and stddevs again.
for num_years in [5,8]:
    partial_means = []
    partial_stddevs = []
    colors = []
    for word in words['new']:
        start = first_appearances[word]
        end = (start[0] + num_years, start[1])
        scores = remove_nones(kl_scores['new'][word][dates.index(start)
                                                     : dates.index(end)])
        if scores != []:
            partial_means.append(np.mean(scores))
            partial_stddevs.append(np.std(scores))
            colors.append(plt.cm.coolwarm((start[0]-1970)/(2000-1970)))
    
    fig, ax = plt.subplots()
    ax.set_axis_bgcolor('0.25')
    ax.scatter(partial_means, partial_stddevs, s=1, color=colors)
    plt.xlabel('Mean KL score of a given word over {} years'.format(num_years))
    plt.ylabel('Standard deviation of KL scores of a given word over {} years'
               .format(num_years))
    plt.savefig('plots/scatter_symKL_partial{}_mean_vs_std_with_yr.png'
                .format(num_years))
    plt.close()
    
    plt.hist(partial_means, bins=70)
    plt.savefig('plots/hist_of_symKL_partial{}_means.png'.format(num_years))
    plt.close()
     
    plt.hist(partial_stddevs, bins=70)
    plt.savefig('plots/hist_of_symKL_partial{}_stddevs.png'.format(num_years))
    plt.close()
 


# Line plot
def error_bars(xs):
    num_samples = 500
    means = sorted([ np.mean(np.random.choice(xs, size=len(xs), replace=True))
                     for i in range(num_samples) ])
    lower_err = means[int(0.01 * num_samples)]
    upper_err = means[int(0.99 * num_samples)]
    return (lower_err, upper_err)

time = [ d[0] + float(d[1]-1)/12 for d in dates ]
old_means = []
old_lower_errs = []
old_upper_errs = []
years = sorted(list(set([ d[0] for d in dates ])))
for year in years:
    scores = []
    for d in [ d for d in dates if d[0] == year ]:
        scores.extend(remove_nones([ kl_scores['old'][word][dates.index(d)]
                                     for word in words['old'] ]))
    mean = np.mean(scores)
    old_means.append(mean)
    errs = error_bars(scores)
    old_lower_errs.append(mean - errs[0])
    old_upper_errs.append(errs[1] - mean)

fig, ax = plt.subplots()
ax.errorbar(years, old_means, yerr=[old_lower_errs, old_upper_errs])
ax.set_xlim([1969, 2010])
plt.savefig('plots/time_series.png')
plt.close()







###############################
# And then do some other stuff:

# The distribution of all KL scores for old words has a strange left hump.
# dump all these words into a file to examine them qualitatively.
left_hump = dict()
for (word,scores) in kl_scores['old'].items():
    for score in remove_nones(scores):
        if 0.5 < score < 0.75:
            if word in left_hump.keys():
                left_hump[word] += 1
            else:
                left_hump[word] = 1
output_filename = 'left_hump_old_words.txt'
with open(output_filename, 'w') as fp:
    for (word, count) in sorted(left_hump.items()):
        fp.write('{}: {}\n'.format(word, count))



# Use a normal distribution to sample words from the two peaks of the
# bimodal distribution of new words.
mean_pairs = []
for word in words['new']:
    scores = remove_nones(kl_scores['new'][word])
    if scores != []:
        mean_pairs.append((np.mean(scores), word))
mean_pairs.sort()
left_peak = 1.9
right_peak = 2.1
stddev = 0.03
num_samples = 400
left_words = set()
right_words = set()

for peak in (left_peak, right_peak):
    for i in range(num_samples):
        r = np.random.randn() * stddev + peak
        for (mean, word) in mean_pairs:
            if mean > r:
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
