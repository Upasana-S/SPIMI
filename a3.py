import csv
from os import listdir
from nltk.tokenize import RegexpTokenizer
from construct_index import spimi_blocks, merge_blocks
'''
tokenizer = RegexpTokenizer(r'\w+') # to remove punctuation
raw_data = open("/home/upasana/AIR/wikipedia-sentences.csv","rb")
csv_data = csv.reader(raw_data, delimiter="\t")
# preprocess the raw-data, tokenise the documents
print("=============== Preprocessing documents... ===============")
documents=[{"url":row[0],"content":tokenizer.tokenize(row[1].lower())} for row in csv_data]
print "Done preprocessing"

block_size=1000000 #1 MB '''
#spimi_blocks(documents, block_size)
blocks = [open('index_blocks/'+block) for block in listdir('index_blocks/')]
print len(blocks)
merge_blocks(blocks)
