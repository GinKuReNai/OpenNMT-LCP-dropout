# 拡張なしの場合に使用する

import sys
import time
import yaml
import re
import os

#与えられたテキストの空白を文字(_)に変え文字ごとのリストに変換
def txt2voc(text):
    #文先頭としてメタ文字'\f'を使用
    w = text.replace(' ','_').replace('\t', '_').replace('\n', '\n\f')
    w = '\f' + w[:-1]
    vocab = ["_" if x == '\f' else "<EOS>" if x == '\n' else x for x in w]
    return vocab

# 与えられたvocabファイルからLCP-dropoutを再現
def lcp_apply(text, merge):
    # 計測開始
    start = time.time()
    # 前処理
    vocab_list = txt2voc(text)
    # 結合段階毎に実行
    i = 1
    for merge_vocab in merge:
        vocab = merge_vocab.split('\n')
        vocab = vocab[:-1]
        # 結合する文字のペアのリスト
        # [(a,b), (ac, d),...]
        merge_pairs = [tuple(x.split()) for x in vocab]
        # 文章から該当ペアのインデックスを取得
        for idx in range(len(vocab_list)):
            # 現在のインデックスのペア
            if '<EOS>' != vocab_list[idx]:
                check_pair = (vocab_list[idx], vocab_list[idx+1])
                # 該当ペアであったなら結合
                if check_pair in merge_pairs:
                    vocab_list[idx] += vocab_list[idx+1]
                    vocab_list[idx+1] = '///'
        # 結合後の後処理
        vocab_list = [x for x in vocab_list if x != '///']
        # 計測終了
        print(i, '/', len(merge), 'merged:', time.time()-start, '[s]')
        i += 1
    return vocab_list

# ディレクトリの自動作成
def make_directory(path):
    # パスをディレクトリとファイルに分離
    re_pattern = re.match('(.*)/(.+\.[a-z]+)', path)
    directory  = re_pattern.group(1)
    
    # 存在しない場合はディレクトリを生成
    os.makedirs(directory, exist_ok=True)

#出力データの整形
def out_file(subword_list, file_name):
    subword = ' '.join(subword_list)
    subword_txt = subword.replace('<EOS>', '\n')
    with open(file_name, 'w') as f:
        f.write(subword_txt)


if __name__=='__main__':
    # 設定ファイルの読み込み
    with open(sys.argv[1], 'r') as yml:
        config = yaml.safe_load(yml)

    with open(config['file']['train'], 'r') as f:
        text = f.read()
    try:
        # vocabファイルから生成されたサブワードを結合毎に獲得
        with open(config['file']['vocab']) as t:
            lines = t.read()
            merge = lines.split('@@@\n')
            merge = merge[:-1]
    except FileNotFoundError:
        merge=[]
    # LCP-dropoutを再現
    subword_list = lcp_apply(text, merge)
    # 出力
    make_directory(config['file']['out'])
    out_file(subword_list, config['file']['out'])
