#!/bin/bash
# 学習モデルから翻訳を行う

#絶対パスを定義
# OpenNMT-tf 設定ファイル
NMT_SETTING_PATH="/home/machine-translation/src/settings/NewsCommentary/de_en/paircomp/k01_l16000_v16000/data_nmt.yml"
# 評価するためのテストデータ
VALID_SOURCE_PATH="/home/machine-translation/src/results/NewsCommentary/de_en/paircomp/k01_l16000_v16000/test/test_de.lcp"
# 翻訳したテストデータを出力するパス
PREDICT_PATH="/home/machine-translation/src/results/NewsCommentary/de_en/paircomp/k01_l16000_v16000/nmt-tf/predict.lcp"

onmt-main --config $NMT_SETTING_PATH --auto_config infer --features_file  $VALID_SOURCE_PATH > $PREDICT_PATH
