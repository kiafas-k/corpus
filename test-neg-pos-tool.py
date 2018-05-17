fl = open('negative-words.txt', 'r')
lines = fl.readlines()
fl.close

words_neg = []


for wrd in lines:
    words_neg.append(wrd.replace('\n', ''))


if 'absurdness' in words_neg:
    print('found negative')
else:
    print('word not found')
