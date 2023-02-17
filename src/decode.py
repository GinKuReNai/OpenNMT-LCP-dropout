from mosestokenizer import *
import sys

directory = sys.argv[1]
suffix    = sys.argv[2]

with open(directory+'predict.'+suffix) as f:
    moses_txt = [t.replace(' ', '').replace('_', ' ').replace('▁', ' ').replace('\n', '') for t in f.readlines()]
token_list = [x.split(' ') for x in moses_txt]
# English:en, German:de, France:fr, Japanese:ja, Chinese:zh
with MosesDetokenizer('en') as detokenize:
    text = [detokenize(x)+'\n' for x in token_list]

with open(directory+'predict.txt', mode='w') as f:
    f.write(''.join(text))
