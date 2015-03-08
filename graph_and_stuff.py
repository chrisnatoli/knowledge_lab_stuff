import csv
import numpy as np
import matplotlib
import matplotlib.pylab as plt
from matplotlib.backends.backend_pdf import PdfPages
import statsmodels.api as sm
import scipy.stats



def string_to_date(s):
    return (int(s[ : len('YYYY')]), int(s[len('YYYY-') : ]))
    
def remove_nones(xs):
    return [ x for x in xs if x is not None ]




# Unpack the table of new words.
new_words_filename = 'new_words.csv'
with open(new_words_filename) as fp:
    reader = csv.reader(fp, delimiter=',')
    new_words_header = next(reader)
    new_words_table = sorted([ row for row in reader ])

# Unpack the table of old words.
old_words_filename = 'old_words.csv'
with open(old_words_filename) as fp:
    reader = csv.reader(fp, delimiter=',')
    old_words_header = next(reader)
    old_words_table = sorted([ row for row in reader ])

# Unpack the table of stopwords.
stopwords_filename = 'stopwords.csv'
with open(stopwords_filename) as fp:
    reader = csv.reader(fp, delimiter=',')
    stopwords_header = next(reader)
    stopwords_table = sorted([ row for row in reader ])

# Unpack total word counts for each month.
counts_filename = 'monthly_word_counts.csv'
monthly_word_counts = dict()
with open(counts_filename) as fp:
    reader = csv.reader(fp, delimiter=',')
    next(reader)
    monthly_word_counts = { string_to_date(row[0]) : int(row[1])
                            for row in reader }
    
# Unpack vocabulary size for each month.
counts_filename = 'monthly_vocab_size.csv'
monthly_vocab_size = dict()
with open(counts_filename) as fp:
    reader = csv.reader(fp, delimiter=',')
    next(reader)
    monthly_vocab_size = { string_to_date(row[0]) : int(row[1])
                           for row in reader }

# Unpack the KL score data and compute means and stddevs for each word.
kls_filename = '_word_symKL_scores.csv'
wordtypes = ['old','new','stop']
words = dict()
kl_scores = dict()
flat_kl_scores = dict()
kl_means = dict()
kl_stddevs = dict()
new_words_left_mode = []
new_words_right_mode = []
for wordtype in wordtypes:
    # Load the data into a dictionary from words to lists of scores.
    kl_scores[wordtype] = dict()
    words[wordtype] = []
    with open(wordtype + kls_filename) as fp:
        dates = [ string_to_date(s) for s in
                  fp.readline().strip().split(',')[1:] ]
        for line in fp:
            tokens = line.strip().split(',')
            word = tokens[0]
            scores = [ float(score) if score != '' else None
                       for score in tokens[1:] ]
            kl_scores[wordtype][word] = scores
            words[wordtype].append(word)
    
    # Generate lists of KL scores, ignoring empty datapoints and
    # words that lack KL scores.
    flat_kl_scores[wordtype] = []
    kl_means[wordtype] = []
    kl_stddevs[wordtype] = []
    for word in words[wordtype]:
        scores = remove_nones(kl_scores[wordtype][word])
        if scores != []:
            flat_kl_scores[wordtype].extend(scores)
            mean = np.mean(scores)
            kl_means[wordtype].append(mean)
            kl_stddevs[wordtype].append(np.std(scores))

            # Also, sort new words according to which mode they're in the
            # bimodal distribution of KL means. The cutoff of 2.04 was
            # eyeballed from the histogram.
            if wordtype == 'new':
                if mean < 2.04:
                    new_words_left_mode.append(word)
                else:
                    new_words_right_mode.append(word)





# Make a simple histogram of the number of new words appearing each month.
date_to_num_new_words = { (y,m):0 for y in range(1970,2000)
                                  for m in range(1,13) }
for word in words['new']:
    for row in new_words_table:
        if row[new_words_header.index('word')] == word:
            date = string_to_date(row[new_words_header.index(
                                      'first appearance')])
            break
    if date in date_to_num_new_words.keys():
        date_to_num_new_words[date] += 1
pairs = sorted(date_to_num_new_words.items())
xs = [ x for (x,y) in pairs ]
ys = [ y for (x,y) in pairs ]
fig, ax = plt.subplots()
ax.bar(range(len(xs)), ys, color='k')
ax.set_xlim([0, len(xs)])
ax.set_xticks([ i for i in range(len(xs)) if i % 12 == 0 ])
ax.set_xticklabels([ '{}-{}'.format(d[0],d[1]) for (i,d) in enumerate(xs)
                     if i % 12 == 0 ],
                   rotation=90)
plt.tick_params(labelsize=8)
plt.xlabel('Time')
plt.ylabel('Number of new words')
plt.tight_layout()
plt.savefig('plots/new_words_per_date.png', dpi=150)
plt.close()



# For both old and new words, plot three histograms:
# - one of all KL scores for all words,
# - one of the mean KL score for each word, and
# - another of stddev of the KL scores for each word.
for wordtype in wordtypes[:2]:
    plt.hist(flat_kl_scores[wordtype], bins=50)
    plt.savefig('plots/hist_of_{}_symKL_scores.png'.format(wordtype))
    plt.close()
    
    plt.hist(kl_means[wordtype], bins=50)
    plt.savefig('plots/hist_of_{}_symKL_means.png'.format(wordtype))
    plt.close()
    
    plt.hist(kl_stddevs[wordtype], bins=50)
    plt.savefig('plots/hist_of_{}_symKL_stddevs.png'.format(wordtype))
    plt.close()



# Make a single scatterplot of tuples (mean, stddev) for
# old words, new words, and stopwords.
for wordtype in wordtypes:
    if wordtype == 'old':
        color = 'b'
        label = 'Old words'
    if wordtype == 'new':
        color = 'r'
        label = 'New words'
    if wordtype == 'stop':
        color = 'g'
        label = 'Stopwords'
    plt.scatter(kl_means[wordtype], kl_stddevs[wordtype],
                s=1, color=color, label=label)
plt.xlabel('Mean KL score of a given word over time')
plt.ylabel('Standard deviation of KL scores for a given word over time')
plt.legend(loc='lower right', prop={'size':8})
plt.savefig('plots/scatter_symKL_mean_vs_std_all_words.png')
plt.close()





# Make multiple scatterplots of tuples (mean, stddev) for only new
# words, where a point is colored by
# -- the time of the word's first appearance,
# -- the term frequency of the word,
# -- the relative term frequency of the word (i.e., raw frequency
#    of the word divided by the number of words in all dates
#    since and including the date of the word's first appearance),
# -- the document frequency of the word (i.e., number of months
#    in which it appeared).
# -- the relative document frequency of the word (i.e., number
#    of months in which it appeared divided by the number of months
#    after and including its first appearance).
coolwarm = plt.cm.coolwarm

first_appearances = dict()
for row in new_words_table:
    word = row[new_words_header.index('word')]
    date = string_to_date(row[new_words_header.index('first appearance')])
    first_appearances[word] = date[0] + (date[1]-1)/12

term_freqs = { row[new_words_header.index('word')]
               : float(row[new_words_header.index('term frequency') ])
               for row in new_words_table }

log_term_freqs = { word : np.log(tf) for (word, tf) in term_freqs.items() }

rel_term_freqs = { row[new_words_header.index('word')]
                   : float(row[new_words_header.index(
                           'relative term frequency') ])
                   for row in new_words_table }

log_rel_term_freqs = { word : np.log(tf) for (word, tf)
                       in rel_term_freqs.items() }

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

for z in [first_appearances, term_freqs, log_term_freqs, rel_term_freqs,
          log_rel_term_freqs, doc_freqs, rel_doc_freqs]:
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
    ax.scatter(kl_means['new'], kl_stddevs['new'], s=1, color=coolwarm(colors))

    m = plt.cm.ScalarMappable(cmap=coolwarm)
    m.set_array(colors)
    cbar = plt.colorbar(m, ticks=[0,1])
    if z == first_appearances:
        cbar.set_ticklabels(['1970','2000'])
    elif z == rel_term_freqs:
        cbar.set_ticklabels(['{0:.4g}'.format(minn), '{0:.4g}'.format(maxx)])
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
    elif z == log_term_freqs:
        cbar.set_label('Log term frequency')
        colored_by = 'ltf'
    elif z == rel_term_freqs:
        cbar.set_label('Relative term frequency')
        colored_by = 'rtf'
    elif z == log_rel_term_freqs:
        cbar.set_label('Log relative term frequency')
        colored_by = 'lrtf'
    elif z == doc_freqs:
        cbar.set_label('Document frequency')
        colored_by = 'df'
    elif z == rel_doc_freqs:
        cbar.set_label('Relative document frequency')
        colored_by = 'rdf'
    plt.savefig('plots/scatter_symKL_mean_vs_std_colored_by_{}.png'
                .format(colored_by))
    plt.close()



# Make two more scatterplots:
# -- plot mean vs std of new, old words, and stopwords colored by
#    term frequency, with the same colormap,
# -- do the same for log term frequency.
old_term_freqs = { row[old_words_header.index('word')]
                   : float(row[old_words_header.index('term frequency')])
                   for row in old_words_table }

log_old_term_freqs = { word : np.log(tf) for (word, tf)
                       in old_term_freqs.items() }

stopword_freqs = dict()
for row in stopwords_table:
    word = row[stopwords_header.index('word')]
    freq = float(row[stopwords_header.index('term frequency')])
    if freq != 0: # If frequency is 0 then log freq = -inf, so drop those. 
        stopword_freqs[word] = freq

log_stopword_freqs = { word : np.log(tf) for (word, tf)
                       in stopword_freqs.items() }

colored_bys = ['tf', 'ltf']
for colored_by in colored_bys:
    fig, ax = plt.subplots()
    for wordtype in ['old', 'new', 'stop']:
        if colored_by == 'tf' and wordtype == 'new':
            z = term_freqs
        elif colored_by == 'ltf' and wordtype == 'new':
            z = log_term_freqs
        elif colored_by == 'tf' and wordtype == 'old':
            z = old_term_freqs
        elif colored_by == 'ltf' and wordtype == 'old':
            z = log_old_term_freqs
        elif colored_by == 'tf' and wordtype == 'stop':
            z = stopword_freqs
        elif colored_by == 'ltf' and wordtype == 'stop':
            z = log_stopword_freqs
        
        # Normalize the color values so that they're in [0,1].
        if colored_by == 'tf':
            minn = min(list(term_freqs.values())
                       + list(old_term_freqs.values())
                       + list(stopword_freqs.values()))
            maxx = max(list(term_freqs.values())
                       + list(old_term_freqs.values())
                       + list(stopword_freqs.values()))
        elif colored_by == 'ltf':
            minn = min(list(log_term_freqs.values())
                       + list(log_old_term_freqs.values())
                       + list(log_stopword_freqs.values()))
            maxx = max(list(log_term_freqs.values())
                       + list(log_old_term_freqs.values())
                       + list(log_stopword_freqs.values()))
        colors = [ (z[word] - minn) / (maxx - minn)
                   for word in words[wordtype]
                   if remove_nones(kl_scores[wordtype][word]) != [] ]

        ax.set_axis_bgcolor('0.25')
        ax.scatter(kl_means[wordtype], kl_stddevs[wordtype], s=1,
                   color=coolwarm(colors))
                   #marker='+' if wordtype=='old' else 'x')

    m = plt.cm.ScalarMappable(cmap=coolwarm)
    m.set_array([0,1])
    cbar = plt.colorbar(m, ticks=[0,1])
    cbar.set_ticklabels(['{0:.2f}'.format(minn), '{0:.2f}'.format(maxx)])
    if colored_by == 'tf':
        cbar.set_label('Term frequency'.format(wordtype))
    elif colored_by == 'ltf':
        cbar.set_label('Log term frequency'.format(wordtype))

    plt.xlabel('Mean KL score of a given word over time')
    plt.ylabel('Standard deviation of KL scores for a given word over time')
    plt.savefig('plots/scatter_symKL_mean_vs_std_colored_by_{}_with_old.png'
                .format(colored_by), dpi=200)
    plt.close()



# Make another scatterplot, but only of old words sampled from the 
# histogram of new word log term frequencies. Color the points by log tf.
xs = []
ys = []
zs = []
sample_size = 4000 # Note that number of unique old words selected < 4000.
new_word_logtfs = sorted(list(log_term_freqs.values()))
old_word_pairs = sorted([ (v,k) for (k,v) in log_old_term_freqs.items() ])
for new_logtf in np.random.choice(new_word_logtfs, size=sample_size):
    for (old_logtf, old_word) in old_word_pairs:
        if old_logtf > new_logtf:
            scores = remove_nones(kl_scores['old'][old_word])
            if scores != []:
                xs.append(np.mean(scores))
                ys.append(np.std(scores))
                zs.append(old_logtf)
                break
            
maxx = max(zs)
minn = min(zs)
colors = [ (z - minn) / (maxx - minn) for z in zs ]

fig, ax = plt.subplots()
ax.set_axis_bgcolor('0.25')
ax.scatter(xs, ys, s=1, color=coolwarm(colors))

m = plt.cm.ScalarMappable(cmap=coolwarm)
m.set_array([0,1])
cbar = plt.colorbar(m, ticks=[0,1])
cbar.set_ticklabels(['{:.2f}'.format(minn), '{:.2f}'.format(maxx)])
cbar.set_label('Log term frequency')
        
plt.xlabel('Mean KL score of a given word over time')
plt.ylabel('Standard deviation of KL scores for a given word over time')

plt.savefig('plots/scatter_symKL_mean_vs_std_old_sample_logtf.png')
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
pdf = PdfPages('plots/scatter_symKL_partial_mean_vs_std_colored_by_yr.pdf')
first_appearances = { row[new_words_header.index('word')]
                      : string_to_date(row[
                          new_words_header.index('first appearance')])
                      for row in new_words_table }
for num_years in range(2,40):
    partial_means = []
    partial_stddevs = []
    colors = []
    for word in words['new']:
        start = first_appearances[word]
        end = (start[0] + num_years, start[1])
        if end > dates[-1]:
            end = dates[-1]
        scores = remove_nones(kl_scores['new'][word][dates.index(start)
                                                     : dates.index(end)])
        if scores != []:
            partial_means.append(np.mean(scores))
            partial_stddevs.append(np.std(scores))
            colors.append(coolwarm((start[0]-1970)/(2000-1970)))
    
    fig, ax = plt.subplots()

    ax.set_axis_bgcolor('0.25')
    ax.scatter(partial_means, partial_stddevs, s=1, color=colors)
    ax.set_xlim([0, 2.5])
    ax.set_ylim([0, 0.5])

    m = plt.cm.ScalarMappable(cmap=coolwarm)
    m.set_array([0,1])
    cbar = plt.colorbar(m, ticks=[0,1])
    cbar.set_ticklabels(['1970','2000'])
    cbar.set_label('First appearance')

    plt.xlabel('Mean KL score of a given word over {} years'.format(num_years))
    plt.ylabel('Standard deviation of KL scores of a given word over {} years'
               .format(num_years))
    plt.savefig(pdf, format='pdf')
    plt.close()

pdf.close()
    




# Use OLS to test if the slopes of the lines for old words, new words,
# and stopwords is the same. Only check dates in [1976,2000).
# Run four regressions:
# -- either the data used for the KL scores of new words is only the scores
#    when words are introduced, or the data covers the entire time series
#    of scores for each new word;
# -- either the only regressor is time or vocab size at each date is used
#    as an additional regressor.
# It is intentional that 'at introduction' 'without vocab' is the
# last regression run, because these slopes and intercepts are used
# for plotting linear fit lines.
regression_output_filename = 'regression_output'
with open(regression_output_filename, 'w') as fp:
    slopes = dict()
    stderrs = dict()
    intercepts = dict()
    num_points = dict()
    which_new_kls = ['after_introduction', 'at_introduction']
    regressions = ['with_vocab', 'without_vocab']
    for which in which_new_kls:
        fp.write('\n\n\n\nKL SCORES FOR NEW WORDS IS {}\n\n'.format(which))
        for regression in regressions:
            fp.write('\n\nTHE FOLLOWING REGRESSION IS {}\n'.format(regression))
            for wordtype in wordtypes:
                # Collect the datapoints from this wordtype.
                scores = []
                times = []
                ds = []
                for word in words[wordtype]:
                    for d in [ d for d in dates if (1976,1) <= d < (2000,1) ]:
                        if (which == 'after_introduction'
                            and wordtype == 'new'
                            and first_appearances[word] != d):
                            continue
                        score = kl_scores[wordtype][word][dates.index(d)]
                        if score is not None:
                            scores.append(score)
                            times.append(d[0] + (d[1]-1)/12)
                            ds.append(d)
                            
                # Fit an OLS model with intercept. Record slope and stderr.
                if regression == 'without_vocab':
                    regressors = times
                elif regression == 'with_vocab':
                    regressors = np.array([times,
                                           [ monthly_word_counts[d] for d in ds ]]).T
                regressors = sm.add_constant(regressors)
                results = sm.OLS(scores, regressors).fit()
                fp.write(str(results.summary()) + '\n\n')

                resids = results.resid
                intercepts[wordtype] = results.params[0]
                slopes[wordtype] = results.params[1]
                stderrs[wordtype] = results.HC0_se[1] # Huber-White
                num_points[wordtype] = len(scores)
                
                plt.scatter(times, [ monthly_vocab_size[d] for d in ds ], s=1)
                plt.savefig('plots/multicollinearity_time_vocab.png')

                plt.scatter([ monthly_word_counts[d] for d in ds ],
                            [ monthly_vocab_size[d] for d in ds ], s=1)
                plt.savefig('plots/multicollinearity_wordcount_vocab.png')

                plt.scatter(times, list(resids), s=1)
                plt.savefig('plots/resid_scatter_{}_{}_{}.png'
                            .format(wordtype, which, regression))
                plt.close()

                sm.qqplot(resids, line='s')
                plt.savefig('plots/resid_qq_{}_{}_{}.png'
                            .format(wordtype, which, regression))
                plt.close()

                (_, bins, _) = plt.hist(resids, 200, normed=1, color='k')
                normal_curve = plt.normpdf(bins, np.mean(resids),
                                           np.std(resids))
                plt.plot(bins, normal_curve, 'r--', linewidth=1.5)
                plt.savefig('plots/resid_hist_{}_{}_{}.png'
                            .format(wordtype, which, regression))
                plt.close()

            # Use a simple t-test to test if the slopes are the same.
            for (i, wordtype_i) in enumerate(wordtypes):
                for (j, wordtype_j) in [ (j,t) for (j,t)
                                         in enumerate(wordtypes) if j>i ]:
                    diff = abs(slopes[wordtype_i] - slopes[wordtype_j])
                    stderr = np.sqrt(stderrs[wordtype_i]**2 
                                     + stderrs[wordtype_j]**2)
                    test_statistic = diff / stderr
                    df = num_points[wordtype_i] + num_points[wordtype_i] - 4
                    p = (1 - scipy.stats.t.cdf(test_statistic, df)) * 2
                    fp.write('Under H_0: slope for {} words = slope for {} words, p-value = {}\n'
                             .format(wordtype_i, wordtype_j, p))





# Time series plot of KL scores:
fig, ax = plt.subplots()
        
# Plot the mean KL scores for three big batches of words
# (where the mean is averaging across words within the batch
# and across a single year):
# -- all old words,
# -- all stopwords,
# -- all new words.
# Also plot error bars for the means, acquired via bootstrapping.

def error_bars(xs, alpha):
    num_samples = 300
    means = sorted([ np.mean(np.random.choice(xs, size=len(xs), replace=True))
                     for i in range(num_samples) ])
    lower_err = np.mean(xs) - means[int(alpha/2 * num_samples)]
    upper_err = means[int((1-alpha/2) * num_samples)] - np.mean(xs)
    return (lower_err, upper_err)

years = sorted(list(set([ d[0] for d in dates if d[0] < 2000 ])))

kl_means_over_words = dict() # Unlike kl_means above, these avg across words.
lower_errs = dict()
upper_errs = dict()

for wordtype in wordtypes:
    # Compute the means and error bars for each wordtype.
    kl_means_over_words[wordtype] = []
    lower_errs[wordtype] = []
    upper_errs[wordtype] = []
    t = []
    for year in years:
        # Rather than plot one point for each month, plot one point for each year.
        # collapsing across the twelve months.
        scores = []
        for d in [ d for d in dates if d[0] == year ]:
            if wordtype == 'old' or wordtype == 'stop':
                scores.extend(remove_nones([ kl_scores[wordtype][word][dates.index(d)]
                                             for word in words[wordtype] ]))
            elif wordtype == 'new':
                new_words_this_month = [ word for word in words['new']
                                         if first_appearances[word] == d ]
                scores.extend(remove_nones([ kl_scores['new'][word][dates.index(d)]
                                             for word in new_words_this_month ]))

        if scores == []:
            kl_means_over_words[wordtype].append(None)
            lower_errs[wordtype].append(None)
            upper_errs[wordtype].append(None)
        else:
            kl_means_over_words[wordtype].append(np.mean(scores))
            errs = error_bars(scores, 0.01)
            lower_errs[wordtype].append(errs[0])
            upper_errs[wordtype].append(errs[1])
            t.append(year)

    # Then plot this batch of words.
    if wordtype == 'old':
        color = 'b'
        label = 'Old words'
    elif wordtype == 'stop':
        color = 'g'
        label = 'Stopwords'
    elif wordtype == 'new':
        color = 'r'
        label = 'New words'

    ax.errorbar(t, remove_nones(kl_means_over_words[wordtype]),
                yerr=[remove_nones(lower_errs[wordtype]),
                      remove_nones(upper_errs[wordtype])],
                linewidth=2, color=color,
                label=label, alpha=0.7)

# Also plot a semitransparent black line for each new word.
for word in words['new']:
    xs = []
    ys = []
    for date in [ d for d in dates if first_appearances[word] <= d < (2000,1) ]:
        score = kl_scores['new'][word][dates.index(date)]
        if score is not None:
            ys.append(score)
            xs.append(date[0] + (date[1]-1)/12)
    if ys != []:
        ax.plot(xs, ys, color='k', alpha=0.005)

# Plot vocabulary size using right y-axis. 
ax2 = ax.twinx()
pairs = sorted(list(monthly_vocab_size.items()))
xs = [ date[0]+(date[1]-1)/12 for (date,size) in pairs ]
ys = [ size for (date,size) in pairs ]
ax2.plot(xs, ys, linewidth=1, color='purple', alpha=0.7,
         label='Vocabulary size')
ax2.set_ylabel('Vocabulary size', color='purple')
for tick in ax2.get_yticklabels():
    tick.set_color('purple')

ax.set_xlabel('Time')
ax.set_ylabel('Symmetric KL divergence')

h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, loc='lower right', prop={'size':8})

ax.set_xlim([1969, 2000])
plt.tight_layout()
plt.savefig('plots/time_series.png', dpi=200)

ax.set_xlim([1976, 2000])
ax.set_ylim([1.2, 2.3])
plt.savefig('plots/time_series_zoom.png', dpi=200)
plt.close()




# Now plot similar graphs but rather than connect the dots between the means,
# just plot the straight lines fitted by OLS.
fig, ax = plt.subplots()

for wordtype in wordtypes:
    # First make a scatterplot with errorbars for each batch of words.
    t = [ year for year in years
          if kl_means_over_words[wordtype][years.index(year)] is not None]
    if wordtype == 'old':
        color = 'b'
        label = r'Old words $\beta_1={:.4f}$'.format(slopes[wordtype])
    elif wordtype == 'stop':
        color = 'g'
        label = r'Stopwords $\beta_1={:.4f}$'.format(slopes[wordtype])
    elif wordtype == 'new':
        color = 'r'
        label = r'New words $\beta_1={:.4f}$'.format(slopes[wordtype])
    ax.errorbar(t, remove_nones(kl_means_over_words[wordtype]),
                yerr=[remove_nones(lower_errs[wordtype]),
                      remove_nones(upper_errs[wordtype])],
                color=color, fmt='', linestyle='None',
                linewidth=2, alpha=0.7)

    # Then add a straight line fitted by OLS.
    xs = [1976, 1999]
    ys = [ intercepts[wordtype] + slopes[wordtype] * x
           for x in xs ]
    ax.plot(xs, ys, color=color, linewidth=2, alpha=0.7, label=label)

plt.legend(loc='lower right', prop={'size':9})

ax.set_xlim([1975, 2000])
ax.set_ylim([1.2, 3.8])

ax.set_xlabel('Time')
ax.set_ylabel('Symmetric KL divergence')

plt.tight_layout()
plt.savefig('plots/time_series_OLSfit.png', dpi=200)
plt.close()
    



# Time series of new words (not averaged) colored by date of first appearance.
fig, ax = plt.subplots()

# First sort the new words by date of first appearance in ascending order.
pairs = sorted([ (first_appearances[word], word) for word in words['new'] ])
sorted_words = [ word for (date, word) in pairs ]
for word in sorted_words:
    first = first_appearances[word]
    scores = []
    ds = []
    for d in [ d for d in dates if d >= first ]:
        score = kl_scores['new'][word][dates.index(d)]
        if score is not None:
            scores.append(score)
            ds.append(d[0] + (d[1]-1)/12)
    first = first[0] + (first[1]-1)/12
    c = matplotlib.colors.rgb2hex(coolwarm((first - 1970) / (2000-1970)))
    if scores != []:
        ax.plot(ds, scores, alpha=0.05, color=c)

m = plt.cm.ScalarMappable(cmap=coolwarm)
m.set_array([0,1])
cbar = plt.colorbar(m, ticks=[0,1])
cbar.set_ticklabels(['1970','2000'])
cbar.set_label('First appearance')

ax.set_axis_bgcolor('0.25')
plt.xlabel('Time')
plt.ylabel('Symmetric KL divergence')

ax.set_xlim([1969, 2000])
plt.savefig('plots/time_series_colored_by_time.png', dpi=200)

ax.set_xlim([1976, 2000])
ax.set_ylim([1.2, 2.3])
plt.savefig('plots/time_series_zoom_colored_by_time.png', dpi=200)
plt.close()









################################
## And then do some other stuff:
#
## The distribution of all KL scores for old words has a strange left hump.
## dump all these words into a file to examine them qualitatively.
#left_hump = dict()
#for (word,scores) in kl_scores['old'].items():
#    for score in remove_nones(scores):
#        if 0.5 < score < 0.75:
#            if word in left_hump.keys():
#                left_hump[word] += 1
#            else:
#                left_hump[word] = 1
#output_filename = 'left_hump_old_words.txt'
#with open(output_filename, 'w') as fp:
#    for (word, count) in sorted(left_hump.items()):
#        fp.write('{}: {}\n'.format(word, count))
#
#
#
## Use a normal distribution to sample words from the two peaks of the
## bimodal distribution of new words.
#mean_pairs = []
#for word in words['new']:
#    scores = remove_nones(kl_scores['new'][word])
#    if scores != []:
#        mean_pairs.append((np.mean(scores), word))
#mean_pairs.sort()
#left_peak = 1.9
#right_peak = 2.1
#stddev = 0.03
#num_samples = 400
#left_words = set()
#right_words = set()
#
#for peak in (left_peak, right_peak):
#    for i in range(num_samples):
#        r = np.random.randn() * stddev + peak
#        for (mean, word) in mean_pairs:
#            if mean > r:
#                if peak == left_peak:
#                    left_words.add(word)
#                else:
#                    right_words.add(word)
#                break
#left_filename = 'left_peak.txt'
#with open(left_filename, 'w') as fp:
#    fp.write('\n'.join(sorted(list(left_words))))
#right_filename = 'right_peak.txt'
#with open(right_filename, 'w') as fp:
#    fp.write('\n'.join(sorted(list(right_words))))
