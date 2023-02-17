from mosestokenizer import *

def tokenizeText(texts, lang):
  """データセットをMosesTokenizerで処理"""
  tokenize = MosesTokenizer(lang)

  tokens = [tokenize(text) for text in texts]
  output = ''
  for token in tokens:
    output += ' '.join(token)+'\n'
  
  return output


def outputFile(path, texts, name, lang):
  """データを出力"""
  with open(path + name + '.' + lang, mode='w') as f:
    f.write(texts)


# 各種パスを設定
directory    = "/home/machine-translation/datasets/WMT14/"
dataset_name = "europarl-v7.de-en"
dataset_path = directory + dataset_name

for lang in ['de', 'en']:
  with open(dataset_path + '.' + lang) as f:
    texts = f.readlines()
  # 行数を記録
  lines = len(texts)

  # 全体の1割をそれぞれ検証およびテストデータに設定
  valid_lines = int(lines / 10)
  test_lines  = int(lines / 10)
  
  # MozesTokenizerで処理
  processed_sentences = tokenizeText(texts, lang)

  # 検証データ、テストデータ、訓練データにそれぞれ分割
  valid = processed_sentences[:valid_lines]
  test  = processed_sentences[valid_lines:(valid_lines+test_lines)]
  train = processed_sentences[(valid_lines+test_lines):]
  
  # directoryにデータを出力
  outputFile(directory, valid, 'valid', lang)
  outputFile(directory, test, 'test', lang)
  outputFile(directory, train, 'train', lang)
