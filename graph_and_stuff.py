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
oldnew = ['old','new']
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
    new_words_left_mode = []
    new_words_right_mode = []
    for word in words[when]:
        scores = remove_nones(kl_scores[when][word])
        if scores != []:
            flat_kl_scores[when].extend(scores)
            mean = np.mean(scores)
            kl_means[when].append(mean)
            kl_stddevs[when].append(np.std(scores))

            # Also, sort words according to which mode they're in in the
            # bimodal distribution of KL means. The cutoff of 2.04 was
            # eyeballed from the histogram.
            if mean < 2.04:
                new_words_left_mode.append(word)
            else:
                new_words_right_mode.append(word)


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



# Make three scatterplots of tuples (mean, stddev) for only new
# words, where a point is colored by
# -- the time of the word's first appearance,
# -- the term frequency of the word,
# -- the document frequency of the word (i.e., number of months
#    in which it appeared).
# -- the relative document frequency of the word (i.e., number
#    of months in which it appeared divided by the number of months
#    after and including its first appearance).
cmap = plt.cm.coolwarm
new_words_filename = 'new_words.csv'
with open(new_words_filename) as fp:
    reader = csv.reader(fp, delimiter=',')
    new_words_header = next(reader)
    new_words_table = sorted([ row for row in csv.reader(fp, delimiter=',') ])

first_appearances = dict()
for row in new_words_table:
    word = row[new_words_header.index('word')]
    date = string_to_date(row[new_words_header.index('first appearance')])
    first_appearances[word] = date[0] + (date[1]-1)/12

term_freqs = { row[new_words_header.index('word')]
               : float(row[new_words_header.index('term frequency') ])
               for row in new_words_table }

doc_freqs = { row[new_words_header.index('word')]
               : float(row[new_words_header.index('num months') ])
               for row in new_words_table }

rel_doc_freqs = dict()
for row in new_words_table:
    word = row[new_words_header.index('word')]
    first = string_to_date(row[new_words_header.index('first appearance')])
    doc_freq = float(row[new_words_header.index('num months')])
    total = len([ d for d in dates if d >= first ]) 
    rel_doc_freqs[word] = doc_freq / total

for z in [first_appearances, term_freqs, doc_freqs, rel_doc_freqs]:
    # Normalize the color values so that they're in [0,1].
    if z == first_appearances:
        minn = 1970
        maxx = 2000
    else:
        minn = min(z.values())
        maxx = max(z.values())
    colors = [ (z[word] - minn) / (maxx - minn)
               for word in words['new']
               if remove_nones(kl_scores['new'][word]) != [] ]
    colors.extend([0, 1])

    fig, ax = plt.subplots()
    ax.set_axis_bgcolor('0.25')
    sc = ax.scatter(kl_means['new'], kl_stddevs['new'], s=1, color=cmap(colors))

    m = plt.cm.ScalarMappable(cmap=cmap)
    m.set_array(colors)
    cbar = plt.colorbar(m, ticks=[0,1])
    if z == first_appearances:
        cbar.set_ticklabels(['1970','2000'])
    else:
        cbar.set_ticklabels(['{0:.2f}'.format(minn), '{0:.2f}'.format(maxx)])

    plt.xlabel('Mean KL score of a given word over time')
    plt.ylabel('Standard deviation of KL scores for a given word over time')
    if z == first_appearances:
        cbar.set_label('First appearance')
        colored_by = 'yr'
    elif z == term_freqs:
        cbar.set_label('Term frequency')
        colored_by = 'tf'
    elif z == doc_freqs:
        cbar.set_label('Document frequency')
        colored_by = 'df'
    elif z == rel_doc_freqs:
        cbar.set_label('Relative document frequency')
        colored_by = 'rdf'
    plt.savefig('plots/scatter_symKL_mean_vs_std_colored_by_{}.png'
                .format(colored_by))
    plt.close()



# More scatterplots: mean vs date of first appearance and stddev vs date.
firsts = [ first_appearances[word] for word in words['new']
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
first_appearances = { row[new_words_header.index('word')]
                      : string_to_date(row[
                          new_words_header.index('first appearance')])
                      for row in new_words_table }
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
            colors.append(cmap((start[0]-1970)/(2000-1970)))
    
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
 


# Time series plot of KL scores for batches of old and new words.
fig, ax = plt.subplots()

def error_bars(xs, alpha):
    num_samples = 300
    means = sorted([ np.mean(np.random.choice(xs, size=len(xs), replace=True))
                     for i in range(num_samples) ])
    lower_err = np.mean(xs) - means[int(alpha/2 * num_samples)]
    upper_err = means[int((1-alpha/2) * num_samples)] - np.mean(xs)
    return (lower_err, upper_err)

years = sorted(list(set([ d[0] for d in dates if d[0] < 2000 ])))
means = dict()
lower_errs = dict()
upper_errs = dict()
lines = ['Old words','New words','Left mode of new words','Right mode of new words']
for line in lines:
    # Compute the means and error bars for each line.
    means[line] = []
    lower_errs[line] = []
    upper_errs[line] = []
    for year in years:
        # Rather than plot one point for each month, plot one point for each year.
        # collapsing across the twelve months.
        scores = []
        for d in [ d for d in dates if d[0] == year ]:
            if line == 'Old words':
                scores.extend(remove_nones([ kl_scores['old'][word][dates.index(d)]
                                             for word in words['old'] ]))
            if line == 'New words':
                new_words_this_month = [ word for word in words['new']
                                         if first_appearances[word] == d ]
                scores.extend(remove_nones([ kl_scores['new'][word][dates.index(d)]
                                             for word in new_words_this_month ]))
            if line == 'Left mode of new words':
                left_words_this_month = [ word for word in new_words_left_mode
                                          if first_appearances[word] == d ]
                scores.extend(remove_nones([ kl_scores['new'][word][dates.index(d)]
                                             for word in left_words_this_month ]))
            if line == 'Right mode of new words':
                right_words_this_month = [ word for word in new_words_right_mode
                                           if first_appearances[word] == d ]
                scores.extend(remove_nones([ kl_scores['new'][word][dates.index(d)]
                                             for word in right_words_this_month ]))
        if scores == []:
            means[line].append(None)
            lower_errs[line].append(None)
            upper_errs[line].append(None)
        else:
            means[line].append(np.mean(scores))
            errs = error_bars(scores, 0.01)
            lower_errs[line].append(errs[0])
            upper_errs[line].append(errs[1])
    
    # Match the time axis to the number of datapoints.
    # I.e., if a datapoint isn't available, skip that year.
    ys = [ y for y in years if means[line][years.index(y)] is not None ]

    ax.errorbar(ys, remove_nones(means[line]),
                yerr=[remove_nones(lower_errs[line]),
                      remove_nones(upper_errs[line])],
                label=line)
                      
    
ax.set_xlim([1969, 2000])
plt.legend(loc='lower right')
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
