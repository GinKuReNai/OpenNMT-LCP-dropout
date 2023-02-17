#!/bin/bash
# dockerコンテナ外で行うこと

# ----------------------

# Deep_Infinity: 131.206.19.137
# Deep_Universe: 131.206.19.143
# Deep_Sirius:   131.206.19.147
# Deep_Capella:  131.206.19.153

# ----------------------

SENDER='a_koga'
RECEIVER='a_koga'
SERVER='131.206.19.147'
DIRECTORY="/home/$SENDER/machine-translation"

# ----------------------

# 単純なディレクトリの同期
rsync -ahvu -e ssh $DIRECTORY $RECEIVER@$SERVER:./

# 指定のファイルの同期
# SENDFILE="/home/$SENDER/machine-translation/src/lcp_revised.py"
# RECEIVELOCATION="/home/$RECEIVER/machine-translation/src/"
# rsync -ahvu -e ssh $SENDFILE $RECEIVER@$SERVER:$RECEIVELOCATION

# 完全なディレクトリの同期
# ※ これは削除を伴うため, 完全に一致させたい場合のみ用いること
# rsync -ahv -e ssh --delete $DIRECTORY $RECEIVER@$SERVER:./

# ----------------------
