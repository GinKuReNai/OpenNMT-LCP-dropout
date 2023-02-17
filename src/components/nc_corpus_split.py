# News Commentary v16のコーパスを訓練用・検証用・テスト用にそれぞれ分割

import random
from mosestokenizer import *

def outputFile(datasetPath, filename, articles):
    """ファイル出力"""
    tokenize_de = MosesTokenizer('de')
    tokenize_en = MosesTokenizer('en')
    de = ''
    en = ''
    for article in articles:
        texts = article.split('\n')
        deen = [x.split('\t') for x in texts[:-1]]
        for t in deen:
            if len(t[0]) != 0 and len(t[1]) != 0:
                de += ' '.join(tokenize_de(t[0]))+'\n'
                en += ' '.join(tokenize_en(t[1]))+'\n'
    with open(datasetPath + filename + '.de', mode='w') as f:
        f.write(de)
    with open(datasetPath + filename + '.en', mode='w') as f:
        f.write(en)

def main(datasetPath):
    # NewsCommentaryデータセットを指定して開く
    with open(datasetPath + 'news-commentary-v16.de-en.tsv') as f:
        texts = f.readlines()

    # 1記事を要素として配列articlesに格納
    articles = []
    article = ''
    for t in texts:
        # 区切り文字を発見したら記事をarticlesに保存して次の記事へ
        if t == '\t\n':
            articles.append(article)
            article = ''
        # 区切り文字でない場合は保存して次の行を読む
        else:
            article += t

    # 記事の順番をシャッフル
    random.shuffle(articles)
    
    # 記事の数を取得
    article_size = len(articles)
    
    # 検証データ・テストデータのサイズをデータセットサイズの1割として計算
    test_size = int(article_size / 10)
    valid_size = int(article_size / 10)

    # 指定した範囲でテスト用・検証用・訓練用に8:1:1の割合で分割する
    test = articles[:test_size]
    valid = articles[test_size:test_size+valid_size]
    train = articles[valid_size:]

    # ファイルを出力する
    outputFile(datasetPath, 'test', test)
    outputFile(datasetPath, 'valid', valid)
    outputFile(datasetPath, 'train', train)

if __name__ == "__main__":
    # データセットの配置場所をここで指定
    datasetPath = '/home/ML/datasets/NewsCommentary/'
    main(datasetPath)
