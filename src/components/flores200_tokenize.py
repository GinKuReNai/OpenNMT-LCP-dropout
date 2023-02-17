# FLORES200データセットの前処理
from mosestokenizer import *
import sys
import re

# データセットのパスを引数から取得
# 例 : python3 flores200_tokenize.py dev/eng_Latn.dev
directory   = "/home/ML/datasets/FLORES200/"
dataset     = sys.argv[1]
input_path  = directory + 'flores200_dataset/' + dataset
output_path = directory + 'processed_data/' + dataset

# mosestokenizerでの言語対応
lang_pattern = {
    'eng': 'en',
    'deu': 'de',
}

# -------------------------------

def tokenize(path, lan):
    """
    テキストの前処理
    """
    with open(path, mode='r') as f:
        texts = f.readlines()

    tokenize = MosesTokenizer(lan)
    # テキストの前処理
    tokens = [tokenize(t) for t in texts]
    output = ''
    for t in tokens:
        output += ' '.join(t)+'\n'

    return output

def output(path, texts):
    """
    処理済みデータの出力
    """
    with open(path, mode='w') as f:
        f.write(texts)

# -------------------------------

re_pattern = re.match('(.*)/(.+\.[a-z]+)', input_path)
filename   = re_pattern.group(2)
re_pattern = re.match('([a-z]+)_([A-Za-z]+)\.[a-z]+', filename)
lang       = re_pattern.group(1)

# 指定のデータセットの前処理
tokenized_texts = tokenize(input_path, lang_pattern[lang])
# 出力処理
output(output_path, tokenized_texts)
