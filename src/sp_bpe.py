# SentencePiece / BPE / BPE-Dropout を実行するコード

import sentencepiece as spm
import sys
import yaml
import time

# パラメータのロード
# ---------------------------------------
with open(sys.argv[1], 'r') as yml:
    config = yaml.safe_load(yml)

# 各種ファイルのPATH
train              = config['file']['train']
valid              = config['file']['valid']
test               = config['file']['test']
prefix             = config['file']['prefix']
model              = config['file']['model']
train_out          = config['file']['train_out']
valid_out          = config['file']['valid_out']
test_out           = config['file']['test_out']
# 各種パラメータ
vocab_size         = config['param']['vocab_size']
character_coverage = config['param']['char_coverage']
model_type         = config['param']['model_type']
alpha              = config['param']['alpha']

# ---------------------------------------

# ---------------------------------------

def encoder(src, model, out):
    """
    テキストをトークナイズして出力
    """
    with open(src, mode='r') as f:
        texts = f.readlines()
    with open(out, mode='w') as f:
        for text in texts:
            piece = sp.encode(text, out_type=str, alpha=alpha, nbest_size=-1)
            for id, token in enumerate(piece):
                f.write(token)
                if id != len(piece):
                    f.write(' ')
            f.write('\n')

# ---------------------------------------

start = time.time()
# make model and vocab file
sp = spm.SentencePieceTrainer.train(
        input=train,
        model_prefix=prefix,
        vocab_size=vocab_size,
        character_coverage=character_coverage,
        model_type=model_type
    )

# sp tokenize
sp = spm.SentencePieceProcessor(model_file=model)

# tokenize
encoder(train, sp, train_out)
encoder(valid, sp, valid_out)
encoder(test, sp, test_out)

print('Finish Time:', time.time() - start, '[s]')
