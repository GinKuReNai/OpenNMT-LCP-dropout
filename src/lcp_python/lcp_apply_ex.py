# パラメータvとlの値が一致していない場合(拡張ありの場合)に使用する

import sys
import os
import re
import time
import yaml
import glob

#---------------------------------------

def txt2voc(text):
    """
    与えられたテキストの空白を文字(_)に変え文字ごとのリストに変換
    """

    #文先頭としてメタ文字'\f'を使用
    w = text.replace(' ','_').replace('\t', '_').replace('\n', '\n\f')
    w = '\f' + w[:-1]
    vocab = ["_" if x == '\f' else "<EOS>" if x == '\n' else x for x in w]
    return vocab

def lcp_apply(text, merge):
    """
    与えられたvocabファイルからLCP-dropoutを再現
    """

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

def rename_first_vocab(vocab):
    """
    先頭のvocabファイル名の末尾に0を追加
    """
    renamed_vocab = vocab + '0'

    if not os.path.exists(renamed_vocab):
        os.rename(vocab, renamed_vocab)
    else:
        return
    
def make_directory(path):
    """
    ディレクトリの自動作成
    """
    # パスをディレクトリとファイルに分離
    re_pattern = re.match('(.*)/(.+\.[a-z]+)', path)
    directory  = re_pattern.group(1)

    # 存在しない場合はディレクトリを生成
    os.makedirs(directory, exist_ok=True)
   

def out_file(subword_list, file_name):
    """
    出力データの整形
    """
    subword = ' '.join(subword_list)
    subword_txt = subword.replace('<EOS>', '\n')
    with open(file_name, 'w') as f:
        f.write(subword_txt)

#---------------------------------------

if __name__=='__main__':

    # 設定ファイルの読み込み
    with open(sys.argv[1], 'r') as yml:
        config = yaml.safe_load(yml)
    
    # 先頭のvocabファイルの末尾に0を追加
    rename_first_vocab(config['file']['vocab'])

    # vocabファイルの数を取得
    vocab_num = len(glob.glob(config['file']['vocab']+'*'))
    print(f'the number of vocab files : {vocab_num}')

    sum_merge = []

    # テストデータの読み込み
    with open(config['file']['train'], 'r') as f:
        text = f.read()

    try:
        # 複数のvocabファイルから取得する
        for i in range(vocab_num):
            # vocabファイルから生成されたサブワードを結合毎に獲得
            with open(config['file']['vocab'] + f'{i}') as t:
                lines = t.read()
                merge = lines.split('@@@\n')
                sum_merge += merge[:-1]
    except FileNotFoundError:
        sum_merge=[]

    # LCP-dropoutを再現
    subword_list = lcp_apply(text, sum_merge)

    # 出力
    make_directory(config['file']['out'])
    out_file(subword_list, config['file']['out'])
