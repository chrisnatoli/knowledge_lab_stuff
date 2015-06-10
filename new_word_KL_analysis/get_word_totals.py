import os

directory = '../data/monthly_abstracts/'
filenames = sorted([ f for f in os.listdir(directory) ])
word_counts_filename = 'monthly_word_counts.csv'
vocab_size_filename = 'monthly_vocab_size.csv'

# Converts '2007-7.txt' to the tuple (2007,7).
def filename_to_date(filename):
    return (int(filename[ : len('YYYY')]),
            int(filename[len('YYYY-') : -len('.txt')]))

def preprocess(text):
    text = text.lower()
    punctuation = (',','"',"'",'.','(',')',':','--','---',
                   '#','[',']','{','}','!','?','$','%',';','/')
    for p in punctuation:
        text = text.replace(p,' {} '.format(p))
    return text

monthly_word_counts = []
monthly_vocab_size = []
for filename in filenames:
    date = filename_to_date(filename)
    with open(directory+filename) as fp:
        words = preprocess(fp.read()).split()
        monthly_word_counts.append([date, len(words)])
        monthly_vocab_size.append([date, len(set(words))])
    print(date)

filenames = (word_counts_filename, vocab_size_filename)
lists = (monthly_word_counts, monthly_vocab_size)
for i in range(len(filenames)):
    lists[i].sort()
    with open(filenames[i], 'w') as fp:
        fp.write('date,num words\n')
        for (date, count) in lists[i]:
            fp.write('{}-{},{}\n'.format(date[0], date[1], count))
