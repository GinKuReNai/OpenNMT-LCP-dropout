#!/bin/bash
# OpenNMT-tfでvocabファイルを作成
# 事前にcopy_lcp.shを実行したあとにmerge_traindata.pyを実行して, train_*_merged.lcpを生成する必要あり

LANG[0]="de"
LANG[1]="en"

VOCAB_SIZE="16000"

# 対象ディレクトリ
DIRECTORY="/home/machine-translation/src/results/NewsCommentary/${LANG[0]}_${LANG[1]}/paircomp/k01_l16000_v16000/"
# DIRECTORY="/home/machine-translation/src/results/FLORES200/deu_eng/sentencepiece/"

# predict.txtを格納するnmt-tfディレクトリがない場合は作成
if [[ ! -d "${DIRECTORY}/nmt-tf" ]]
then
  mkdir "${DIRECTORY}/nmt-tf"
fi

# vocabファイルの作成
for lang in ${LANG[@]}; do
  # LCP(拡張あり)
  # INPUT="${DIRECTORY}train/train_${lang}_merged.lcp"
  # OUTPUT="${DIRECTORY}nmt-tf/vocab_${lang}_merged.txt"

  # LCP(拡張なし)
  INPUT="${DIRECTORY}train/train_${lang}.lcp"
  OUTPUT="${DIRECTORY}nmt-tf/vocab_${lang}.txt"

  # sentencepiece / bpe / bpe-dropout(bped)
  # OUTPUT="${DIRECTORY}vocab_${lang}.txt"
  # VOCAB="${DIRECTORY}sp_${lang}.vocab"

  onmt-build-vocab --size $VOCAB_SIZE --save_vocab $OUTPUT $INPUT
  # onmt-build-vocab --from_vocab $VOCAB --from_format sentencepiece --save_vocab $OUTPUT

done
