# load the_words.csv

from array import array
import csv
from re import sub


fandom_words = {}
permitted = set()

print("copy over the_words.csv")
with open('the_words.csv', 'r') as f:
    csv_reader = csv.reader(f)
    for k, v in csv_reader:
        fandom_words[k] = v


with open('test_adj.txt', 'r') as f:
    for line in f.readlines():
        permitted.add(line.strip())

print("copy over test noun.txt")
with open('test_noun.txt', 'r') as f:
    for line in f.readlines():
        permitted.add(line.strip())

print("req size",len(permitted))
print('happy' in permitted)

counter = 0
max = len(fandom_words)

to_delete_words = []
for line in fandom_words.keys():
    if line not in permitted:
        sub_line = line
        sub_found = False
        while sub_line != '' and abs(len(line) - len(sub_line)) < len(line) // 2 :
            sub_line = sub_line[:-1]
            if sub_line in permitted:
                sub_found = True
                break
        if not sub_found: 
            to_delete_words.append(line)
        counter += 1
print("ones removed:",counter)
print('eradication',counter / max)

for line in to_delete_words:
    del fandom_words[line]


with open('the_words_filtered.csv', 'w') as f:
    csv_writer = csv.writer(f, lineterminator='\n')
    for k, v in fandom_words.items():
        csv_writer.writerow([k, v])


# if 