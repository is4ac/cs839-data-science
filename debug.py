from collections import Counter
import operator
import csv

words_false_positive = []
words_false_negative = []

with open('stage1_docs/Data/results.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['class_label'] == '0':
            words_false_positive.append(row['string'])
        else:
            words_false_negative.append(row['string'])

counts_positive = Counter(words_false_positive)
counts_negative = Counter(words_false_negative)
#print(counts_positive)
#print(counts_negative)
sorted_counts = sorted(counts_negative.items(), key=operator.itemgetter(1))
whitelist = ''
for (key, value) in sorted_counts:
    if value == 2:
        whitelist = whitelist + ("'%s'," % key)
print whitelist
