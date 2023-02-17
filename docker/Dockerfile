# Tensorflowをベースにコンテナを生成
# NVIDIA GPU対応コンテナを生成
FROM tensorflow/tensorflow:2.9.0-gpu
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# コンテナ内にディレクトリmachine-translationを作成し作業ディレクトリに変更
RUN mkdir machine-translation
WORKDIR /home/machine-translation

# requirements.txtを作業ディレクトリにコピーしてaptの実行
COPY ./docker/requirements.txt /home/machine-translation/

# Pythonのパッケージをインストール
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install --upgrade requests

# C++の開発環境を構築
RUN apt-get update
RUN apt-get install -y build-essential cmake clang texinfo gdb

# datasetsディレクトリをコピー
RUN mkdir datasets
# srcディレクトリをコピーして作業ディレクトリに変更
WORKDIR /home/machine-translation/src/
