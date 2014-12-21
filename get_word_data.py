import csv
import os

input_filename = 'log9all0.9'
directory = 'monthly_abstracts/'
filenames = sorted([ f for f in os.listdir(directory) ])

monthly_text = dict()
for filename in filenames:
    date = (int(filename[ : len('YYYY')]),
            int(filename[len('YYYY-') : -len('.txt')]))

    with open(directory+filename) as fp:
        text = fp.read().lower()
        punctuation = (',','"',"'",'.','(',')',':','--','---',
                       '#','[',']','{','}','!','?','$','%',';')
        for p in punctuation:
            text = text.replace(p,' {} '.format(p))
        monthly_text[date] = text

    print('Reading in text for '+filename)

print('Finished reading in all text')

dates = sorted(monthly_text.keys())

with open(input_filename) as fp:
    lines = fp.readlines()
    new_words = lines[-2][1:-2].replace("'","").split(', ')
new_words.sort()

header = ['word', 'first appearance', 'term freqency', 'num months']
table = [header]
for word in new_words:
    print('Getting data for "{}"'.format(word))

    first_appearance = None
    frequency = 0
    num_months = 0
    for date in dates:
        if word in monthly_text[date]:
            if first_appearance is not None:
                first_appearance = date
            frequency = frequency + monthly_text[date].count(word)
            num_months = num_months + 1
    table.append([word, '{}-{}'.format(date[0],date[1]),
                  frequency, num_months])

output_filename = 'new_words.csv'
with open(output_filename, 'w', newline='') as fp:
    writer = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(table)

print('fin')

