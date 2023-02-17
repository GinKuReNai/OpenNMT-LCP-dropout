# ニューラル機械翻訳

ニューラル機械翻訳に関する研究について, LCP-dropout, Tensorflowで動作するOpenNMT-tf および その他ツールが含まれた開発環境です.

## インストール方法
### Getting Started

研究を始めるにあたり, 手元の環境に実行環境をデプロイする手順を説明します.

1. このリポジトリをクローンします. `git clone git@gitlab.com:kit-ai-sakamoto-lab/machine-translation.git`

2. machine-translationディレクトリに移動し, Dockerコンテナを立ち上げます. `docker-compose up -d --build`

3. Dockerコンテナ内に入ります. `docker exec -it nmt bash`

4. コンテナ内でプログラムの実行などを行ってください.

### YAML-CPP

C++のプログラムを実行するには, [yaml-cpp](https://github.com/jbeder/yaml-cpp)の手動インストールが必要です.

1. Dockerコンテナ(nmt)内でlcp_cpp内のyaml-cppのインストーラが入った圧縮ファイルを解凍します. `tar -zxvf ./lcp_cpp/yaml-cpp-yaml-cpp-0.6.0.tar.gz`

2. フォルダに移動します. `cd yaml-cpp-yaml-cpp-0.6.0`

3. buildディレクトリを作成します. `mkdir build`

4. buildディレクトリに移動して, cmakeを実行する. `cmake ..`

5. buildディレクトリ内でmakeを実行する. `make`

6. そのままインストール `make install`

lcp_cpp内のMakefileを用いてコンパイルすれば, YAML-CPPを使用したコンパイルをすることができます.

## 実行例

### コンパイル

C++のコードをコンパイルする場合, Makefileが使用できます. makeコマンドは以下の通りです.

- `make` : 全てのプログラムをコンパイル

- `make lcp_random` : `lcp_random.cpp`をコンパイル

- `make lcp_paircomp` : `lcp_paircomp.cpp`をコンパイル

- `make lcp_paircomp_faster` : `lcp_paircomp_faster.cpp`をコンパイル

- `make clean` : 全てのオブジェクトコードを削除

### LCP-dropoutの実行

#### 訓練データに対するLCP-dropout

LCP-dropoutを実行する際は, コマンドライン引数として対応する設定ファイルを指定してください.

C++での例: `./lcp_paircomp /home/machine-translation/src/settings/NewsCommentary/de_en/paircomp/k01_l16000_v16000/config_en_train.yml`

Pythonでの例: `python3 lcp_paircomp.py /home/machine-translation/src/settings/NewsCommentary/de_en/paircomp/k01_l16000_v16000/config_en_train.yml`

設定ファイルで指定した出力ファイルのディレクトリは自動作成されるように実装しているため, 事前の作成は不要です.

設定ファイル`config_(lang)_(train / valid / test).yml`で指定するパラメータは以下の通りです.

- `train`: LCP-dropoutを適用する訓練データ

- `pref`: ランダムな処理で生成したシード値のリスト. このシード値を用いることで, 別ファイルでの動作の再現が可能.

- `vocab`: 2-gramの結合したペアを保存したリスト. このファイルを用いることで, 訓練データでの割り振りを検証データやテストデータに対しても適用できる.

- `out`: 最終的にサブワード分割を行ったテキストの出力先

- `csv`: 処理回数と生成したサブワード数のペアを保存するCSVファイル. 生成されるサブワード数の追跡や, エラー時の分析に使用できる. ※出力したい場合のみ記述

- `time`: 処理時間を保存するテキストファイル. 処理時間の計測や分析に使用できる. ※出力したい場合のみ記述

- `k`: 抽出する出現頻度上位の確率. 

- `l`: 1回の分割パターンで生成するサブワード数

- `v`: 全体の処理で生成するサブワード数

- `d`: dropout率 (ただし, dropout率は0.0が望ましい)

この設定ファイルはsettingsディレクトリ以下にあります.

### 検証データ, テストデータに対するLCP-dropout 

OpenNMT-tfでの学習には検証データ, テストデータに対するLCP-dropoutが必要です. 訓練データと同じ生成ペアで処理するために, 拡張なしの場合は`lcp_apply.py`, 拡張ありの場合は`lcp_apply_ex.py`を用いて処理を行います.

検証データでの実行例: `python3 lcp_apply.py /home/machine-translation/src/settings/NewsCommentary/de_en/paircomp/k01_l16000_v16000/config_en_valid.yml`

テストデータでの実行例: `python3 lcp_apply.py /home/machine-translation/src/settings/NewsCommentary/de_en/paircomp/k01_l16000_v16000/config_en_test.yml`

### OpenNMT-tfを用いた学習の実行

LCP-dropoutにより各種ファイルが出力された後, OpenNMT-tfを用いて学習を行い, 学習モデルを生成します.

- データ拡張を行わない場合 (`l`と`v`の値が等しいとき)
    1. `components/onmt-build-vocab.sh`の中身を任意の形式にコメントアウト等で修正し, `./onmt-build-vocab.sh`として実行.
    
    2. `components/onmt-main-train.sh`の中身を任意の形式にコメントアウト等で修正し, `nohup ./onmt-main-train.sh &`として実行. (実行時間が非常にかかるため, nohupコマンドを用いてバックグラウンドで実行すること)
    
    3. `components/onmt-main-translate.sh`の中身を任意の形式にコメントアウト等で修正し, `./onmt-main-translate.sh`として実行.
    
- データ拡張を行う場合 (`l`と`v`の値が異なるとき)
    データ拡張を行う場合は, 複数の分割パターンファイルを1つに結合し, それに対して学習を実行します. そのため, 以下の手順が追加で必要です. それ以外はデータ拡張を行わない場合と同様です.

    1. `copy_and_merge_lcp.sh`の任意の形式にコメントアウト等で修正し, `./copy_and_merge_lcp.sh`として実行. 出力ファイルとして, `vocab_(lang)_merged.lcp`という名前のファイルが出力されます.

    2. 出力されたファイルに対して, `onmt-build-vocab.sh`を実行します. コメントアウト等で拡張ありの処理に変更し, `./onmt-build-vocab.sh`として実行.

    3. それ以降はデータ拡張なしの2. の手順以降と同様.
    
シェルスクリプト内部に記述されている, OpenNMT-tfのコマンドについては, [lcp-dropoutのリポジトリ](https://gitlab.com/kit-ai-sakamoto-lab/lcp-dropout)や[ドキュメント](https://opennmt.net/OpenNMT-tf/)を参照してください.

### SacreBLEUを用いた翻訳性能の評価

`components/sacrebleu.sh`の中身を任意の形式にコメントアウト等で修正し, `./sacrebleu.sh`として実行します. CharF2++スコアについては, データセットが小さくBLUEスコアが出ない場合に使用してください.

### サーバー間のデータ転送

この研究はDockerを用いて実行環境を実装しており, 複数のサーバーで簡単に実行可能です. 生成した学習モデルなど, 容量等の関係でGitLabで管理できないものについては`components/resync.sh`の中身を任意の形式にコメントアウト等で修正し, `./rsync.sh`として実行してください.

## 含まれるプログラムの紹介
### src/components

componentsディレクトリには, 研究を進める上でよく実行するコマンドを集めたシェルスクリプトや, データセットの処理に関する細かいツールが含まれています.

- `onmt-build-vocab.sh` : 学習に必要なvocabファイルを生成するツール

- `onmt-main-train.sh` : 学習を行うツール

- `onmt-main-translate.sh` : 学習モデルを用いて, テストデータを翻訳するツール

- `sacrebleu.sh` : SacreBLEUを実行し, 翻訳性能を出力するツール

- `rsync.sh` : サーバー間でデータ共有を行うためのツール

- `copy_and_merge_lcp.sh` : データ拡張した際に出力される複数の分割パターンファイルを, 翻訳先と翻訳元の行数が同数になるように整えながら, 一つのテキストファイルにマージするためのツール

- `count_vocab.py` : 任意のテキストファイル内の単語数を計測するツール

- `flores200_tokenize.py` : FLORES200データセットをMosesTokenizerで前処理するためのツール

- `kftt_corpus_split.py` : KFTTデータセットを訓練データ, 検証(開発)データ, テストデータに分割するツール

- `merge_traindata.py` : テキストをマージするためのツール. (通常copy_and_merge_lcp.shから呼び出されるので, 手動で実行することはない)

- `nc_corpus_split.py` : NewsCommentaryデータセットを訓練データ, 検証(開発)データ, テストデータに分割するツール

- `opus-euconst_split.py` : OpusEuconstデータセットをHugging Faceから取得し, 訓練データ, 検証(開発)データ, テストデータに分割するツール

### src/lcp_cpp

lcp_cppディレクトリには, C++20で実装されたLCP-dropoutのプログラムが含まれています.

- `main.cpp` : main関数

- `lcp_utility.cpp` : lcpの処理を補完する自作ユーティリティ関数群

- `lcp_random.cpp` : 符号をランダムで割り振りするLCP-dropout

- `lcp_paircomp.cpp` : PairCompression-based LCP-dropout (Original)

- `lcp_paircomp_faster.cpp` : PairCompression-based LCP-dropout (データ構造による高速化済)

- `Makefile` : コンパイルするためのMakefile (コンパイルフラグとリンクフラグは削除しないように)

### src/lcp_python

lcp_pythonディレクトリには, Python3で実装されたLCP-dropoutのプログラムが含まれています.

- `lcp_random.py` : 符号をランダムで割り振りするLCP-dropout

- `lcp_paircomp.py` : PairCompression-based LCP-dropout (Original)

- `lcp_apply.py` : 訓練データに対してLCP-dropoutを実行した際の単語割り振りを, 検証データやテストデータでも再現する

- `lcp_apply_ex.py` : データ拡張し複数の分割パターンファイルが出力された際に, 検証データやテストデータで再現する

### その他

- `decode.py` : メタ文字"_"入りテキストを自然な文にデコードするツール(components/sacrebleu.shから呼び出されるので, 手動で実行することはない)

- `sp_bpe.py` : BPE, BPE-dropout, SentencePieceを実行するツール

## 使用技術・ライブラリ

使用した技術・ライブラリの一覧です.

- [Docker](https://www.docker.com/)

- [yaml-cpp](https://github.com/jbeder/yaml-cpp)

- [OpenNMT-tf](https://github.com/OpenNMT/OpenNMT-tf)

- [SacreBLEU](https://github.com/mjpost/sacrebleu)

- [MosesTokenizer](https://pypi.org/project/mosestokenizer/)

- [SentencePiece](https://github.com/google/sentencepiece)

## 注意

サーバーへのssh接続を行ってから, サーバー上で本リポジトリをクローンしてください.
また, 学習モデルのサイズは巨大になることが予想されるため, 適宜.gitignoreを作成してコミットに含めないようにしてください.

Dockerコンテナ上で仮想的な実行環境を構築しているため, Dockerの知識は推奨されますが, なくても支障はありません.
C++とPythonのスキルは必須です.

## 参考文献

- サブワード分割に関する説明 : https://www.slideshare.net/ssuserd79a5c1/2019bpe
 
- OpenNMT-tf Documentation : https://opennmt.net/OpenNMT-tf/#

- BPE-dropout : https://aclanthology.org/2020.acl-main.170/

- Hugging Face (新規のデータセットを見つけるときはここがすごく便利) : https://huggingface.co/

- 2019年の先行研究 : https://gitlab.com/kit-ai-sakamoto-lab/thesis2019/-/tree/master/tanaka

- 2021年の先行研究 : https://gitlab.com/kit-ai-sakamoto-lab/thesis2021/-/tree/main/M2_Nonaka

- 2022年の先行研究 : 

## おわりに

何かわからないことがある場合は, 古賀までSlackで連絡してください.
