import sys
import time
from time import perf_counter
import yaml
import random
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
    
# 開始するアルファベットをランダムに選択
def choice_start_alphabet(alphabets, pref):
    # 現在時刻をシード値として使用
    time = str(perf_counter())

    if pref == "":
        seed_value = time
    else:
        seed_value = pref
    
    # シード値から疑似乱数を生成
    random.seed(seed_value)
    
    # 疑似乱数に基づいて開始文字を選択
    alphabet = random.choice(alphabets)

    # 開始文字とシード値を返却
    return alphabet, seed_value

# 符号割り振りの初期化処理
def initialize_zeroone_list(vocab, alphabets):
    # vocabと対応する符号を格納する配列
    zeroone_list = []
    for vi in range(len(vocab)):
        # メタ文字_が含まれるサブワードに1を付与
        if '_' in vocab[vi]:
            zeroone_list.append(1)
            # アルファベット∑から未削除のメタ文字入サブワードを除外
            if vocab[vi] in alphabets:
                alphabets.remove(vocab[vi])
        # End of Sentence(<EOS>)に2を付与
        elif '<EOS>' == vocab[vi]:
            zeroone_list.append(2)
            # アルファベット∑から未削除の<EOS>を除外
            if '<EOS>' in alphabets:
                alphabets.remove('<EOS>')
        # その他の文字には未割当符号3を付与
        else:
            zeroone_list.append(3)
    
    return zeroone_list, alphabets

# PairCompressionのアルゴリズムに基づいたラベルの付与
def pair_compression_to_zeroone(vocab, alphabets, pref, pref_name):
    # 符号割り振りの初期化処理
    zeroone_list, alphabets = initialize_zeroone_list(vocab, alphabets)

    # アルファベット∑からランダムに1文字を選択
    start_word, start_word_seed = choice_start_alphabet(alphabets, pref)
    
    print("開始文字 : " + start_word)
    
    # 既存のシード値がない場合（新規の場合）
    if pref == "":
        # シード値start_word_seedをprefファイルに保存
        with open(pref_name, mode='a') as t:
            t.write(start_word_seed + '\n')
        
    # 開始文字の符号を0に設定
    zeroone_list = [0 if vocab[vi] == start_word else zeroone_list[vi] for vi in range(len(vocab))]

    #アルファベット∑から開始文字を除外
    alphabets.remove(start_word)

    # 2-gram生成の基準文字（開始文字）
    point = start_word

    # 全ての文字にラベルが付与されたら終了
    while(len(alphabets)):
        zero_sigma = 0  # x∑0 or ∑0xの頻度
        one_sigma  = 0  # x∑1 or ∑1xの頻度
        
        print(f"アルファベット∑の要素数 : {len(alphabets)}")
        
        # 基準文字の右隣の文字x∈∑となるパターンが存在することを示すフラグ
        pattern_find_flg = 0

        # 基準文字の右隣の文字xを探索
        for vi in range(len(vocab)-1):
            if vocab[vi] == point and vocab[vi+1] in alphabets:
                target = vocab[vi+1]
                pattern_find_flg = 1
                print("右隣の文字 : " + target)
                break
            
        # パターンが見つかった場合
        if pattern_find_flg:
            # x? or ?x となるような2-gramを探索する
            for vi in range(len(vocab)-1):
                # x? or ?x となるような2-gramが見つかった場合
                if vocab[vi] == target or vocab[vi+1] == target:
                    # x? の場合
                    if vocab[vi] == target:
                        if zeroone_list[vi+1] == 0:
                            zero_sigma += 1
                        if zeroone_list[vi+1] == 1:
                            one_sigma += 1
                    # ?x の場合
                    if vocab[vi+1] == target:
                        if zeroone_list[vi] == 0:
                            zero_sigma += 1
                        if zeroone_list[vi] == 1:
                            one_sigma += 1

            # 条件に合わせて対象文字に 0 or 1 を付与
            if zero_sigma >= one_sigma:
                zeroone_list = [1 if vocab[vi] == target else zeroone_list[vi] for vi in range(len(vocab))]
            else:
                zeroone_list = [0 if vocab[vi] == target else zeroone_list[vi] for vi in range(len(vocab))]

            #アルファベット∑から対象文字を除外
            alphabets.remove(target)

            # 基準文字を対象文字に変更
            point = target
        # パターンが見つからなかった場合
        else:
            print("パターンが見つかりませんでした。")
            # ラベルが割り振られていない語彙を先頭から探索してその手前の文字を基準文字に設定
            for vi in range(len(vocab)-1):
                if vocab[vi] in alphabets:
                    point = vocab[vi-1]
                    break

    return zeroone_list

# "01"になるパターンの位置を返す
def get_01pairs(vocab, zeroone_lst, topk):
    # key:2-gram, value:出現回数
    pairs_dict = {}
    # key:2-gram, value:[vocab中でのインデックス]
    pairs_idx = {}

    # 文字列の探索
    for i in range(len(vocab)-1):
        # ラベル列が 01 となる部分を探索
        if zeroone_lst[i] == 0 and zeroone_lst[i+1] == 1:
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
def merge_vocab(vocab, pairs_idx, dropout_rate):
    # 2-gramの前の文字に後の文字を結合，後の文字は削除
    for idx in pairs_idx:
        # dropout率に基づいて結合を制御
        if (random.random() > dropout_rate):
            vocab[idx] = vocab[idx] + vocab[idx+1]
            vocab[idx+1] = '///'
    # 2-gramの後の文字を削除
    vocab = [x for x in vocab if x != '///']
    return vocab


# LCP本体
def lcp(text, pref, pref_name, time_address, topk, voc_size, dropout_rate):
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

        # 文書中の出現文字の集合を取得
        alphabets = list(set(vocab))

        # PairCompressionアルゴリズムにしたがってラベル1or0の付与
        if not pref:
            zeroone_list = pair_compression_to_zeroone(vocab, alphabets, "", pref_name)
        else:
            zeroone_list = pair_compression_to_zeroone(vocab, alphabets, pref[i], pref_name)

        # ラベル 01 を探索し出現回数を計測
        pairs_idx, merge_pairs = get_01pairs(vocab, zeroone_list, topk=topk)
        # 01 となる2-gramを結合
        vocab = merge_vocab(vocab, pairs_idx, dropout_rate)
        # 結合した2-gramの保存
        save_pairs.append([x+' '+y+'\n' for (x, y) in merge_pairs])
        merge_counter = len(set(vocab))
        
        # 1度のラベル付与->結合までの時間計測の終了
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
def lcp_dropout(train_address, pref_address, vocab_address, out_address, time_address, topk, voc_size, dropout_rate):
    # LCP-dropoutを適用する文章
    with open(train_address, 'r') as f:
        text = f.read()

    #prefの確認
    try:
        with open(pref_address) as t:
            lines = t.read()
            pref  = lines.splitlines()
    except FileNotFoundError:
        pref=[]

    # LCP本体
    subword_list, save_pairs = lcp(text, pref, pref_address, time_address, topk, voc_size, dropout_rate)

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
    voc_all      = config['param']['v']
    # 1度の実行における語彙サイズ l
    # todo: lを可変量にする実装
    voc_size     = config['param']['l']
    # top k
    topk         = config['param']['k']
    # dropout率
    dropout_rate = 0.0
    if 'd' in config['param']:
        dropout_rate = config['param']['d']

    # 1度目のLCP実行
    subword_set = lcp_dropout(train_address, pref_address, vocab_address, out_address, time_address, topk, voc_size, dropout_rate)
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
