#!/bin/bash
# 翻訳元ファイルと翻訳先ファイルが同数になるまで複製する

DIRECTORY="/home/machine-translation/src/results/NewsCommentary/de_en/lcp-dropout/k01_l6000_v16000/train/"
SRC_LANG="de"
TGT_LANG="en"

SRC_LCP_PATH="${DIRECTORY}train_${SRC_LANG}.lcp"
TGT_LCP_PATH="${DIRECTORY}train_${TGT_LANG}.lcp"


# 先頭のlcpファイル名の末尾に0を追加
if [[ -f $SRC_LCP_PATH ]]
then
  mv $SRC_LCP_PATH ${SRC_LCP_PATH}0
fi
if [[ -f $TGT_LCP_PATH ]]
then
  mv $TGT_LCP_PATH ${TGT_LCP_PATH}0
fi


#各ファイル数を取得
#翻訳元ファイル数
SRC_FILE_NUM=$(ls $SRC_LCP_PATH* | wc -l)
#翻訳先ファイル数
TGT_FILE_NUM=$(ls $TGT_LCP_PATH* | wc -l)


if [ "$SRC_FILE_NUM" -lt "$TGT_FILE_NUM" ]
then
  FITEE=$SRC_FILE_NUM
  FITER=$TGT_FILE_NUM
  
  FITEE_PATH=$SRC_LCP_PATH
else
  FITEE=$TGT_FILE_NUM
  FITER=$SRC_FILE_NUM
  
  FITEE_PATH=$TGT_LCP_PATH
fi


# fiteeがfiterと同数になるまで複製する
for ((i = 0; i + $FITEE < $FITER; i++)); do
  cp ${FITEE_PATH}${i} ${FITEE_PATH}$((i + FITEE))
done

# 翻訳元ファイルと翻訳先ファイルを1つのファイルにマージ
python3 /home/machine-translation/src/components/merge_traindata.py $DIRECTORY $SRC_LANG $TGT_LANG
