# LCPでデータ拡張を行った際に, train.lcp*を全て足し合わせる
# NewsCommentary(De - En)
import os
import sys

directory = sys.argv[1]
src_lang  = sys.argv[2]
tgt_lang  = sys.argv[3]

file_name = directory + '/train_'
language  = [src_lang, tgt_lang]
extension = '.lcp'  # 拡張子

for lang in language:
    text = ''

    k = 0
    while(os.path.isfile(file_name+lang+extension+str(k))):
        with open(file_name+lang+extension+str(k)) as f:
            text += f.read()
        k += 1

    with open(file_name+lang+'_merged'+extension, mode='w') as f:
        f.write(text)
