import sys
import time
from time import perf_counter
import yaml
import re
import os
import csv

# 与えられたテキストの空白をメタ文字(_)に変え1文字単位で分割(1文字ごとのリストに変換)
def txt2voc(text):
    # 各文先頭にはメタ文字'\f'を挿入
    w = text.replace(' ','_').replace('\t', '_').replace('\n', '\n\f')
    w = '\f' + w[:-1]
    #　各文の終わりに End Of Sentence を挿入
    vocab = ["_" if x == '\f' else "<EOS>" if x == '\n' else x for x in w]
    return vocab


# Hash関数で0,1を付与
class Hash01:
    # prefファイルを用いてランダムな分割の再現性を確保
    def __init__(self):
        self.t = str(perf_counter())

    # 文末尾には2(分割に関与しない), メタ文字を含むなら1, それ以外なら0or1
    def __call__(self, c: str):
        if '<EOS>' == c:
            return 2, self.t
        elif '_' in c:
            return 1, self.t
        else:
            return hash(c + self.t) & 1 , self.t

# 既存のprefファイルを用いる時はこっちが動作
def call01(c, pref):
    if '<EOS>' == str(c):
        return 2
    elif '_' in str(c):
        return 1
    else:
        return hash(c + str(pref)) & 1


# Hash関数を基に文字毎のリストに対しラベルを付与
def random_zeroone(vocab, *pref):
    # prefファイルの新規作成
    if not pref:
        h = Hash01()
        zeroone_lst = [h(x)[0] for x in vocab]
        return zeroone_lst, h('a')[1]
    # 既存のprefファイルを用いた場合
    else:
        zeroone_lst = [call01(x, pref) for x in vocab]
        return zeroone_lst, pref


# "10"になるパターンの位置を返す
def get_10pairs(vocab, zeroone_lst, topk):
    # key:2-gram, value:出現回数
    pairs_dict = {}
    # key:2-gram, value:[vocab中でのインデックス]
    pairs_idx = {}

    # 文字列の探索
    for i in range(len(vocab)-1):
        # ラベル列が 10 となる部分を探索
        if zeroone_lst[i] == 1 and zeroone_lst[i+1] == 0:
            # 2-gram
            pairs = (vocab[i], vocab[i+1])
            # 既存パターンをカウントしインデックスを追加
            if pairs in pairs_dict.keys():
                pairs_dict[pairs] = pairs_dict[pairs] + 1
                pairs_idx[pairs].append(i)
            # 新パターン追加
            else:
                pairs_dict[pairs] = 1
                pairs_idx[pairs] = [i]

    # topk%を満たす2-gramのインデックスのリスト
    top_idx = []
    # 結合する2-gramの数をtopkから計算
    merge_num = int(len(pairs_dict) * topk / 100)

    # pairs_dictを出現回数の多い順にソート
    sorted_counter = sorted(pairs_dict.items(), key=lambda x:x[1], reverse=True)

    # topkを満たす2-gramのインデックスをtopk_idxに格納
    # topkを満たす2-gramリスト
    merge_pairs = [x[0] for x in sorted_counter]
    merge_pairs = merge_pairs[:merge_num]
    # 上の2-gramリストを基に出現したインデックスを獲得
    for pair in merge_pairs:
        top_idx.extend(pairs_idx[pair])
    top_idx.sort()
    # topkを満たす2-gramのインデックスリスト，その2-gramリスト
    return top_idx, merge_pairs


# 指定されたインデックスに基づき2-gramを結合
def merge_vocab(vocab, pairs_idx):
    # 2-gramの前の文字に後の文字を結合，後の文字は削除
    for idx in pairs_idx:
        vocab[idx] = vocab[idx] + vocab[idx+1]
        vocab[idx+1] = '///'
    # 2-gramの後の文字を削除
    vocab = [x for x in vocab if x != '///']
    return vocab


# LCP本体
def lcp(text, pref, pref_name, time_address, topk, voc_size):
    #計測開始
    start = time.perf_counter()
    # 単語間の空白をメタ文字に変換し1文字単位に分割
    vocab = txt2voc(text)

    # ラベルの付与回数
    i = 0
    # 結合した2-gramの数
    merge_counter = 0
    # その2-gramのリスト
    save_pairs = []
    # 指定した語彙サイズ l を満たすまで実行
    while merge_counter  <= voc_size:
        # 1度のラベル付与->結合までの時間計測の開始
        start_merge = time.perf_counter()
        # ラベル1or0の付与
        if not pref:
            zeroone_lst, zeroone_time = random_zeroone(vocab)
            # prefファイルを保存
            with open(pref_name, 'a') as t:
                t.write(zeroone_time + "\n")
        #既存のprefを用いると"10"を再現可能
        else:
            zeroone_lst, zeroone_time = random_zeroone(vocab, pref[i])

        # ラベル 10 を探索し出現回数を計測
        pairs_idx, merge_pairs = get_10pairs(vocab, zeroone_lst, topk=topk)
        # 10 となる2-gramを結合
        vocab = merge_vocab(vocab, pairs_idx)
        # 結合した2-gramの保存
        save_pairs.append([x+' '+y+'\n' for (x, y) in merge_pairs])
        merge_counter = len(set(vocab))
        
        # 1度のラベル付与->結合までの時間計測の開始
        end_merge = time.perf_counter()
        merge_time = end_merge - start_merge

        print(merge_counter, 'words merged')
        print("merge_finish_time:", merge_time, '[s]')
        print('***************')
        
        # 1度のラベル付与->結合までの時間をファイルに出力
        if not time_address == '':
            with open(time_address, 'a') as f:
                f.write(f"{merge_time}\n")

        i += 1

    #計測終了
    end = time.perf_counter()
    period = end - start

    print("lcp finish", period, '[s]')
    print(i, 'times merged')
    
    if not time_address == '':
        with open(time_address, 'a') as f:
            f.write(f"{period}\n\n")

    # 結合した文, 結合した2-gramリスト
    return vocab, save_pairs

# LCP実行
def lcp_dropout(train_address, pref_address, vocab_address, out_address, time_address, topk, voc_size):
    # LCP-dropoutを適用する文章
    with open(train_address, 'r') as f:
        text = f.read()
    #prefの確認
    try:
        with open(pref_address) as t:
            lines = t.read()
            pref = lines.splitlines()
    except FileNotFoundError:
        pref=[]
    # LCP本体
    subword_list, save_pairs = lcp(text, pref, pref_address, time_address, topk, voc_size)
    # データの出力
    out_file(subword_list, save_pairs, vocab_address, out_address)
    # 1度のLCPで作成されたサブワード集合
    return set(subword_list)


# 出力データの整形
def out_file(subword_list, save_pairs, vocab_name, out_name):
    subword = ' '.join(subword_list)
    subword_txt = subword.replace('<EOS>', '\n')
    with open(out_name, 'w') as f:
        f.write(subword_txt)
    # 結合した2-gramをvocabファイルに保存
    with open(vocab_name, mode='w') as f:
        for p in save_pairs:
            f.write(''.join(p))
            f.write('@@@\n')
            
# ディレクトリの自動作成
def make_directory(path):
    # パスをディレクトリとファイルに分離
    re_pattern = re.match('(.*)/(.+\.[a-z]+)', path)
    directory  = re_pattern.group(1)

    # 存在しない場合はディレクトリを生成
    os.makedirs(directory, exist_ok=True)

# CSVファイルの生成
def out_csv(csv_file, param):
    with open(csv_file, mode='a') as cf:
        writer = csv.writer(cf)
        writer.writerow(param)

# 合計サブワード数を標準出力
def out_num_of_subword(num):
    print('===============')
    print(f'合計サブワード数 : {num}')
    print('===============')

# サブワード分割処理結果を出力処理
def output_segmentation_result(csv_file, pattern_num, subword_num):
    # 合計サブワード数を標準出力
    out_num_of_subword(subword_num)
    # CSVファイルに合計サブワード数を出力
    if not csv_file == '':
        param = [pattern_num, subword_num]
        out_csv(csv_file, param)


if __name__=='__main__':
    # 設定ファイルの読み込み
    with open(sys.argv[1], 'r') as yml:
        config = yaml.safe_load(yml)

    # ファイル名の設定
    train_address = config['file']['train']
    pref_address  = config['file']['pref']
    vocab_address = config['file']['vocab']
    out_address   = config['file']['out']
    csv_address   = ''
    time_address  = ''
    if 'csv' in config['file']:
        csv_address = config['file']['csv']
    if 'time' in config['file']:
        time_address = config['file']['time']
    
    # ディレクトリの自動生成
    make_directory(train_address)
    make_directory(pref_address)
    make_directory(vocab_address)
    make_directory(out_address)
    if not csv_address == '':
        make_directory(csv_address)
    if not time_address == '':
        make_directory(time_address)

    # 全体の語彙サイズ v
    voc_all  = config['param']['v']
    # 1度の実行における語彙サイズ l
    voc_size = config['param']['l']
    # top k
    topk     = config['param']['k']

    # 1度目のLCP実行
    subword_set = lcp_dropout(train_address, pref_address, vocab_address, out_address, time_address, topk, voc_size)
    # LCP結果を出力処理
    output_segmentation_result(csv_address, 0, len(subword_set))
    # 出力する分割パターン数
    j = 1

    # 各実行で生成されたサブワード数が全体の語彙サイズを満たすまでLCPを実行
    while(len(subword_set) < voc_all):
        # 適用毎に出力ファイル名を変更
        pref_address  = config['file']['pref'] + str(j)
        vocab_address = config['file']['vocab'] + str(j)
        out_address   = config['file']['out'] + str(j)
        # LCP実行
        new_set = lcp_dropout(train_address, pref_address, vocab_address, out_address, time_address, topk, voc_size)
        # 和集合で全体の語彙に加える
        # 生成したサブワードの重複を取り除くために和集合で演算を行う
        subword_set = subword_set | new_set

        # LCP結果を出力処理
        output_segmentation_result(csv_address, j, len(subword_set))

        j += 1
