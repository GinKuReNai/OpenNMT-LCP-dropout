#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_set>
#include <vector>
#include <tuple>
#include <regex>
#include <chrono>
#include <functional>
#include <unordered_map>
#include "lcp_utility.hpp"

using namespace std;

// pair<T, U>をキーとする連想配列の定義は, ハッシュ関数が未定義のため定義できない
// pair<T, U>に対するハッシュ関数を手動で定義
namespace std
{
    template <typename T, typename U>
    struct hash<pair<T, U>>
    {
        size_t operator()(const pair<T, U> &p) const
        {
            return hash<T>()(p.first) ^ hash<U>()(p.second);
        }
    };
}

const hash<string> Hasher;

// 与えられたテキストの空白をメタ文字(_)に変え1文字単位で分割（1文字ごとのリストに変換）
static vector<string> txt2voc(string text)
{
    vector<string> vocab;
    const size_t hashEmp = Hasher(" ");
    const size_t hashTab = Hasher("\t");
    const size_t hashClear = Hasher("\f");
    const size_t hashNewline = Hasher("\n");

    for (char c : text)
    {
        // char c を{c}でstd::stringに変換して, std::hash<std::string>でハッシュ値に変換
        size_t hashWord = Hasher({c});

        // 時間計算量が大きいので, ハッシュ値の比較を用いて高速化
        if (hashWord == hashEmp || hashWord == hashTab || hashWord == hashClear)
        {
            vocab.push_back("_");
        }
        else if (hashWord == hashNewline)
        {
            vocab.push_back("<EOS>");
            vocab.push_back("_");
        }
        else
        {
            vocab.push_back({c});
        }
    }

    return vocab;
}

// ハッシュ関数を基に01を生成
static inline int hash01(string const &subword, size_t const &seed)
{
    const size_t hashEos = Hasher("<EOS>");
    size_t hashSubword = Hasher(subword);
    int label = (hashSubword + seed) & 1;

    // 新規のシード値から01を生成
    if (hashSubword == hashEos)
    {
        return 2;
    }
    else if (subword.find("_") != string::npos)
    {
        return 1;
    }

    return label;
}

// シード値を基にランダムにラベルを付与
static tuple<vector<int>, size_t> assembleRandomZeroone(
    vector<string> const &vocab,
    size_t const &pref)
{
    int label;
    size_t seed;
    vector<int> zerooneList;

    // シード値timeを生成
    size_t time = generateHighResolutionClock();

    (pref == -1) ? (seed = time) : (seed = pref);

    // サブワード毎に01の付与
    for (const auto &subword : vocab)
    {
        label = hash01(subword, seed);
        zerooneList.push_back(label);
    }

    return {zerooneList, seed};
}

// "10"になるパターンの位置を返す
static tuple<vector<pair<string, string>>, vector<int>> get10Pairs(
    vector<string> const &vocab,
    vector<int> const &zerooneList,
    int const topk)
{
    // key:ペア, value:ペアの出現頻度
    unordered_map<pair<string, string>, int> pairToFreqMap;
    // key:ペア, value:[vocab中での出現位置(index)]
    unordered_map<pair<string, string>, vector<int>> pairToIndexMap;

    // 文字列の探索
    for (int i = 0; i < (vocab.size() - 1); i++)
    {
        // ラベル列が 10 となる部分を探索
        if (zerooneList[i] == 1 && zerooneList[i + 1] == 0)
        {
            // ペア
            pair<string, string> pair = {vocab[i], vocab[i + 1]};

            // ペアが既に出現している場合
            if (pairToFreqMap.count(pair))
            {
                pairToFreqMap[pair] = pairToFreqMap[pair] + 1;
                pairToIndexMap[pair].push_back(i);
            }
            // 新パターンを追加
            else
            {
                pairToFreqMap.insert({pair, 1});
                pairToIndexMap[pair] = {i};
            }
        }
    }

    // topk(%)を満たすペアのインデックスのリスト
    vector<int> topkIncludeIndexes;

    // 結合するペアの数をtopkから計算
    int mergeNum = static_cast<int>(pairToFreqMap.size() * topk / 100);

    // pairToFreqMapを出現回数の多い順にソート
    vector<pair<pair<string, string>, int>> orderedPairToFreqMap = sortMapByDescOrder(pairToFreqMap);

    // topkを満たすペアのインデックスをtopkIncludeIndexesに格納
    vector<pair<string, string>> topkIncludePairs;
    for (int index = 0; index < mergeNum; index++)
    {
        topkIncludePairs.push_back(orderedPairToFreqMap[index].first);
    }

    // topkIncludePairsを基に出現したインデックスを獲得
    for (pair<string, string> pair : topkIncludePairs)
    {
        topkIncludeIndexes.insert(
            topkIncludeIndexes.end(),
            pairToIndexMap[pair].begin(),
            pairToIndexMap[pair].end());
    }
    // topkIncludeIndexesを昇順にソート
    sort(topkIncludeIndexes.begin(), topkIncludeIndexes.end());

    // topkを満たすペアとインデックスを返却
    return {topkIncludePairs, topkIncludeIndexes};
}

// 指定されたインデックスに基づいてペアを結合
static void mergeVocab(
    vector<string> &vocab,
    vector<int> const &topkIncludeIndexes)
{
    // 対象のペアの前の文字に次の文字を結合して, 後の文字を削除
    for (int index : topkIncludeIndexes)
    {
        vocab[index] = vocab[index] + vocab[index + 1];
        vocab[index + 1] = "///";
    }

    // ペアの後の文字を削除(ここの動作少し危ないかも)
    vocab.erase(remove(vocab.begin(), vocab.end(), "///"), vocab.end());
}

// LCP-Dropout（ランダムに符号を割り振り）
static tuple<vector<string>, vector<vector<string>>> lcpDropout(
    string const &text,
    vector<size_t> const &prefList,
    string const &prefAddress,
    string const &timeAddress,
    int const topk,
    int const vocSize,
    double const dropoutRate)
{
    // 計測開始
    auto lcpDropoutStartTime = chrono::high_resolution_clock::now();

    // 単語間の空白をメタ文字に変換し1文字単位に分割
    vector<string> vocab = txt2voc(text);

    // ラベルの付与回数
    int lcpLoopCount = 0;
    // 結合したペアの数
    int mergedPairCount = 0;
    // 結合したペアのリスト
    vector<vector<string>> mergedPairs;

    // 指定した語彙サイズ l(vocSize) を満たすまで繰り返す
    while (mergedPairCount <= vocSize)
    {
        vector<int> zerooneList;
        size_t zerooneSeed;

        // 一度のラベル付与から結合までの実行時間計測の開始
        auto startTime = chrono::high_resolution_clock::now();

        // 既存のシード値がない場合
        if (prefList.empty())
        {
            // 新規シード値からラベル1or0の付与
            tie(zerooneList, zerooneSeed) = assembleRandomZeroone(vocab, -1);

            // 新規シード値をprefファイルに書き込み
            ofstream ofs;
            ofs.open(prefAddress, ios::app);
            ofs << zerooneSeed << endl;
        }
        // 既存のシード値が存在する場合
        else
        {
            // 既存のシード値からラベル1or0の付与
            tie(zerooneList, zerooneSeed) = assembleRandomZeroone(vocab, prefList[lcpLoopCount]);
        }

        // ラベル 10 を探索し出現回数を計測
        vector<pair<string, string>> topkIncludePairs;
        vector<int> topkIncludeIndexes;
        tie(topkIncludePairs, topkIncludeIndexes) = get10Pairs(vocab, zerooneList, topk);

        // 10 となる
        mergeVocab(vocab, topkIncludeIndexes);

        // 結合したペアの保存
        vector<string> mergedPairsElement;
        for (pair<string, string> pair : topkIncludePairs)
        {
            // 結合して文字列にしたペアを保存
            mergedPairsElement.push_back(pair.first + " " + pair.second + "\n");
        }
        mergedPairs.push_back(mergedPairsElement);

        // ペア数を更新
        unordered_set<string> setVocab(vocab.begin(), vocab.end());
        mergedPairCount = setVocab.size();

        // 一度のラベル付与から結合までの時間を計算
        auto endTime = chrono::high_resolution_clock::now();
        auto processedTime = chrono::duration_cast<chrono::duration<double>>(endTime - startTime);

        // 処理状況を標準出力
        cout << mergedPairCount << "words merged" << endl;
        cout << "merge_finish_time : " << processedTime.count() << "[s]" << endl;
        cout << "*****************" << endl;
        
        // 一度のラベル付与から結合までの時間をファイルに出力
        ofstream ofs;
        ofs.open(timeAddress, ios::app);
        ofs << processedTime.count() << endl;

        lcpLoopCount++;
    }

    // LCP-Dropout全体の処理時間を計算
    auto lcpDropoutEndTime = chrono::high_resolution_clock::now();
    auto lcpTime = chrono::duration_cast<chrono::duration<double>>(lcpDropoutEndTime - lcpDropoutStartTime);

    // 計測終了
    cout << "lcp finish : " << lcpTime.count() << "[s]" << endl;
    cout << lcpLoopCount << "times merged" << endl;
    
    // LCP-Dropout全体の処理時間をファイルに出力
    ofstream ofs;
    ofs.open(timeAddress, ios::app);
    ofs << lcpTime.count() << endl;

    return {vocab, mergedPairs};
}

// LCPの実行
unordered_set<string> lcp(
    string const &trainAddress,
    string const &prefAddress,
    string const &vocabAddress,
    string const &outAddress,
    string const &timeAddress,
    int const topk,
    int const vocSize,
    double const dropoutRate)
{
    vector<size_t> prefList;
    vector<string> subwordList;
    vector<vector<string>> mergedPairs;
    string line;

    // LCP-Dropoutを適用する文章を読み込み
    ifstream train(trainAddress);
    if (!train)
    {
        cerr << "LCP-Dropoutを適用する訓練データが見つかりません." << endl;
        exit(1);
    }

    // 文章を一括で文字列としてtrainTextに格納
    istreambuf_iterator<char> it(train);
    istreambuf_iterator<char> last;
    string trainText(it, last);

    // prefファイルの確認
    ifstream pref(prefAddress);
    if (pref)
    {
        // 既存のシード値を1行ずつ読み込み
        while (getline(pref, line))
        {
            prefList.push_back(stoull(line));
        }
    }

    // LCP-Dropoutの呼び出し
    tie(subwordList, mergedPairs) = lcpDropout(trainText, prefList, prefAddress, timeAddress, topk, vocSize, dropoutRate);

    // 結果の出力
    outputResults(subwordList, mergedPairs, vocabAddress, outAddress);

    // 一度のLCPで作成されたサブワード集合
    unordered_set<string> subwordSet(subwordList.begin(), subwordList.end());

    return subwordSet;
}
