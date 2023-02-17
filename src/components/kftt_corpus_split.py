# KFTT(The Kyoto Free Translation Task）のコーパスを訓練用・検証用・テスト用にそれぞれ分割
import random
from mosestokenizer import *

def out_file(filename, lan):
    with open('/dat/datasets/text/kftt/kftt-data-1.0/data/orig/kyoto-'+filename+'.'+lan) as f:
        texts = f.readlines()
    tokenize = MosesTokenizer(lan)
    tokens = [tokenize(t) for t in texts]
    output = ''
    for t in tokens:
        output += ' '.join(t)+'\n'
    with open(filename+'.'+lan, mode='w') as f:
        f.write(output)

def main():
    out_file('train', 'ja')
    out_file('train', 'en')
    out_file('dev', 'ja')
    out_file('dev', 'en')
    out_file('test', 'ja')
    out_file('test', 'en')

if __name__ == "__main__":
    main()
