#!/bin/bash
# OpenNMT-tfでモデルのディープラーニングを行う

#絶対パスを定義
NMT_SETTING_PATH="/home/machine-translation/src/settings/NewsCommentary/de_en/paircomp/k01_l16000_v16000/data_nmt.yml"
# NMT_SETTING_PATH="/home/machine-translation/src/settings/NewsCommentary/de_en/sentencepiece/data_nmt.yml"

#GPU数: Deep Capellaは2つ
GPU_NUM=1

#学習
onmt-main --model_type Transformer --config ${NMT_SETTING_PATH} --auto_config train --with_eval --num_gpus ${GPU_NUM}
