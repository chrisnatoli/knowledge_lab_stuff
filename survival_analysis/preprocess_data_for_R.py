import csv

input_filename = "dead_words_with_kl.csv"
output_filename = "dead_words_with_kl_interpolated.csv"

data = []
with open(input_filename) as fp:
    reader = csv.reader(fp, delimiter=',')
    header = next(reader)
    for row in reader:
        word = row[header.index('word')]
        time_origin = row[header.index('time origin')]
        time_origin_index = header.index(time_origin)
        end_point = row[header.index('end point')]

        # Linearly interpolate between each non-missing datapoint.
        not_missing = [ index for index in range(len(row))
                        if index >= time_origin_index and row[index] != '' ]
        for j in range(len(not_missing)-1):
            left_index = not_missing[j]
            right_index = not_missing[j+1]
            n = right_index - left_index

            left_value = float(row[left_index])
            right_value = float(row[right_index])

            increment = (right_value - left_value) / n
            for k in range(n):
                kl_score = left_value + k * increment
                data.append([word, left_index - 3, right_index - 3,
                             1 if header[right_index] == end_point else 0,
                             kl_score])

with open(output_filename, 'w') as fp:
    writer = csv.writer(fp, delimiter=',')
    writer.writerow(['word', 'time1', 'time2', 'status', 'kl score'])
    writer.writerows(data)
