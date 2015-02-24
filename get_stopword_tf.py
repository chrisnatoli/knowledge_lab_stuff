import os
from datetime import datetime

the_beginning = datetime.now()

directory = 'monthly_abstracts/'
corpus_filenames = sorted([ f for f in os.listdir(directory) ])
stopwords_filename = 'stopwords.txt'
output_filename = 'stopwords.csv'

def preprocess(text):
    text = text.lower()
    punctuation = (',','"',"'",'.','(',')',':','--','---',
                   '#','[',']','{','}','!','?','$','%',';','/')
    for p in punctuation:
        text = text.replace(p,' {} '.format(p))
    return text
    


# Read in a set of stop words.
stopwords = []
with open(stopwords_filename) as fp:
    for line in fp:
        word = line.strip()
        if word != '':
            stopwords.append(word)

# Collect the term frequencies of stopwords from each file.
table = [ [word, 0] for word in stopwords ]
for filename in corpus_filenames:
    start_time = datetime.now()

    with open(directory+filename) as fp:
        words = preprocess(fp.read()).split()

    for row in table:
        row[1] += words.count(row[0])

    print('Term frequencies were collected from {} in {}'
          .format(filename, datetime.now()-start_time))

table.sort()
table.insert(0, ['word', 'term frequency'])
with open(output_filename, 'w') as fp:
    for row in table:
        fp.write('{},{}\n'.format(row[0], row[1]))
