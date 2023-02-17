# OpusEuconstデータセットをHuggingFaceからダウンロードするプログラム
from datasets import load_dataset
from mosestokenizer import *

# --------------------------------

class FetchOpusEuconstDataset:
    """
    Hugging Faceの'OpusEuconst'対英訳データセットを取得するクラス
    """
    def __init__(self):
        self._name     = 'opus_euconst'
        self._src_lang = ['cs',   # チェコ語(Czech)
                         'da',   # デンマーク語(Danish)
                         'de',   # ドイツ語(Germany)
                         'el',   # ギリシャ語(Greek)
                         'es',   # スペイン語(Spanish)
                         'et',   # エストニア語(Estonian)
                         'fi',   # フィンランド語(Finnish)
                         'fr',   # フランス語(French)
                         'ga',   # アイルランド語(Irish)
                         'hu',   # ハンガリー語(Hungarian)
                         'it',   # イタリア語(Italian)
                         'lt',   # リトアニア語(Lithuanian)
                         'lv',   # ラトビア語(Latvian)
                         'mt',   # マルタ語(Maltese)
                         'nl',   # オランダ語(Dutch)
                         'pl',   # ポーランド語(Polish)
                         'pt',   # ポルトガル語(Portuguese)
                         'sk',   # スロバキア語(Slovak)
                         'sl',   # スロベニア語(Slovenian)
                         'sv',   # スウェーデン語(Swedish)
                         ]
        
    def getName(self):
        """
        メンバ変数'_name'を取得
        """
        return self.name
   
    
    def getSrcLang(self):
        """
        メンバ変数'_src_lang'を取得
        """
        return self._src_lang
    


    def getText(self, lang):
        """
        指定言語の対訳テキストを取得
        
        lang  : 取得する言語コード
        """
        # データセットを取得
        if lang in ['cs', 'da', 'de', 'el']:
            dataset = load_dataset(self._name, f'{lang}-en')
        else:
            dataset = load_dataset(self._name, f'en-{lang}')

        rows = dataset.num_rows['train']
        data = dataset['train'][:rows]['translation']
        
        text_list    = []
        text_list_en = []

        for d in data:
            text_list.append(d[lang])
            text_list_en.append(d['en'])
        
        return text_list, text_list_en


    def tokenize(self, lang, texts):
        """
        MosesTokenizerで前処理
        
        lang : 処理する言語コード
        texts: テキストが格納された配列
        """
        text_list = []
        tokenize  = MosesTokenizer(lang)

        # 1行ずつ前処理して配列に格納
        for text in texts:
            tokens = [tokenize(text)]
            
            processed = ''
            for t in tokens:
                processed += ' '.join(t) + '\n'
                text_list.append(processed)

        return text_list


    def output(self, filename, texts):
        """
        テキストを出力
        
        filename: 出力するファイル名
        texts   : テキストが格納された配列
        """
        with open(filename, mode='w') as f:
            for text in texts:
                f.write(text)


def allProcessHundler(lang):
    """
    取得から出力まで処理を行うハンドラ
    """
    # ファイル名    
    output_path = '/home/machine-translation/datasets/OpusEuconst/'
    train    = output_path + f'train/train_{lang}-en_{lang}.dev'
    valid    = output_path + f'valid/valid_{lang}-en_{lang}.devtest'
    test     = output_path + f'test/test_{lang}-en_{lang}.test'
    train_en = output_path + f'train/train_{lang}-en_en.dev'
    valid_en = output_path + f'valid/valid_{lang}-en_en.devtest'
    test_en  = output_path + f'test/test_{lang}-en_en.test'

    # データセットからテキストを取得
    texts, texts_en = dataset_helper.getText(lang)

    # テキストの前処理
    processed    = dataset_helper.tokenize(lang, texts)
    processed_en = dataset_helper.tokenize('en', texts_en)
    
    train_num = int(0.8 * len(processed))
    valid_num = int(0.1 * len(processed))

    # データ出力
    dataset_helper.output(train, processed[:train_num])
    dataset_helper.output(valid, processed[train_num:train_num + valid_num])
    dataset_helper.output(test, processed[-valid_num:])

    dataset_helper.output(train_en, processed_en[:train_num])
    dataset_helper.output(valid_en, processed_en[train_num:train_num + valid_num])
    dataset_helper.output(test_en, processed_en[-valid_num:])

# --------------------------------

dataset_helper = FetchOpusEuconstDataset()
# 対英訳テキストの取得
for lang in dataset_helper.getSrcLang():
    allProcessHundler(lang)
