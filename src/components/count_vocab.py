# 文書中の総単語数を計測

def count_vocab(data):
    """
    データセットの総単語数を算出
    """
    with open(data, mode='r') as f:
        text = f.read()
    vocab_list = text.split()
    
    return len(set(vocab_list))

data = '/home/machine-translation/datasets/NewsCommentary/processed_data/de_en/train.en'
# data = '/home/machine-translation/datasets/FLORES200/flores200_dataset/dev/eng_Latn.dev'
# data = '/home/machine-translation/datasets/OpusEuconst/train/train_lt-en_en.dev'

vocab_size = count_vocab(data)
print(f'単語数 : {vocab_size}')
