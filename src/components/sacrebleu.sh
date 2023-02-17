#!/bin/bash
# BLEUスコアを算出する

# DIRECTORY, SUFFIXは毎回確認すること

TESTDATA_PATH="/home/machine-translation/datasets/NewsCommentary/processed_data/de_en/test.en"
# TESTDATA_PATH="/home/machine-translation/datasets/FLORES200/flores200_dataset/devtest/eng_Latn.devtest"
# TESTDATA_PATH="/home/machine-translation/datasets/OpusEuconst/test/test_de-en_en.test"
DIRECTORY="/home/machine-translation/src/results/NewsCommentary/de_en/lcp-kai-dropout/k01_l16000_v16000/nmt-tf/"
# DIRECTORY="/home/machine-translation/src/results/NewsCommentary/de_en/bpe-dropout/nmt-tf/"
PREDICT_PATH="${DIRECTORY}predict.txt"
SUFFIX="lcp" # lcp / sp / bpe / bped

# 翻訳結果のデコード
python3 /home/machine-translation/src/decode.py $DIRECTORY $SUFFIX
# BLEUスコアの算出
sacrebleu $TESTDATA_PATH < $PREDICT_PATH
# ChrF2++スコアの算出
# sacrebleu -m chrf --chrf-word-order 2 $TESTDATA_PATH < $PREDICT_PATH
