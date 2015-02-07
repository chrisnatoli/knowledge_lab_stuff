import os

directory = 'monthly_abstracts/'
filenames = sorted([ f for f in os.listdir(directory) ])
output_filename = 'monthly_counts.csv'

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
 
monthly_counts = []
for filename in filenames:
    date = filename_to_date(filename)
    with open(directory+filename) as fp:
        count = len(preprocess(fp.read()).split())
        monthly_counts.append([date, count])
    print(date)

monthly_counts.sort()

with open(output_filename, 'w') as fp:
    fp.write('date,num words\n')
    for (date, count) in monthly_counts:
        fp.write('{}-{},{}\n'.format(date[0], date[1], count))
