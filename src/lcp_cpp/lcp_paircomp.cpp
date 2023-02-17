/**
 * @file lcp_paircomp.cpp
 * @author Akito Koga (koga.akito893@mail.kyutech.jp)
 * @brief PairCompression-based LCP-Dropout (Original)
 * @version 0.1
 * @date 2023-02-14
 *
 * @copyright Copyright (c) 2023
 *
 */

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_set>
#include <set>
#include <vector>
#include <tuple>
#include <chrono>
#include <functional>
#include <unordered_map>
#include <random>
#include <list>
#include "lcp_utility.hpp"

using namespace std;

// pair<T, U>をキーとする連想配列の定義は, ハッシュ関数が未定義のため定義できない
// pair<T, U>に対するハッシュ関数を手動で定義
namespace std
{
    /**
     * @brief 自作ハッシュ関数
     *
     * @tparam T
     * @tparam U
     */
    template <typename T, typename U>
    struct hash<pair<T, U>>
    {
        size_t operator()(const pair<T, U> &p) const
        {
            return hash<T>()(p.first) ^ hash<U>()(p.second);
        }
    };
}

const hash<string> Hasher; /* stringに対するハッシュ関数 */
size_t seed;               /* シード値をグローバル変数で保持 */

/**
 * @brief 与えられたテキストの空白をメタ文字(_)に変え1文字単位で分割（1文字ごとのリストに変換）
 *
 * @param text string_view
 * @return vector<string>
 */
static vector<string> txt2voc(string_view text)
{
    vector<string> vocab;
    const size_t hashEmp = Hasher(" ");
    const size_t hashTab = Hasher("\t");
    const size_t hashClear = Hasher("\f");
    const size_t hashNewline = Hasher("\n");

    for (char c : text)
    {
        string word{c};

        size_t hashWord = Hasher(word);

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
            vocab.push_back(word);
        }
    }

    return vocab;
}

/**
 * @brief 開始するアルファベットをランダムに選択
 *
 * @param alphabets set<string>
 * @param pref size_t
 * @return string
 */
static string choiceStartAlphabet(
    set<string> const &alphabets,
    size_t const &pref)
{
    // 現在時刻を生成
    size_t time = generateHighResolutionClock();

    // シード値を決定
    (pref == -1) ? (seed = time) : (seed = pref);

    // 疑似乱数生成エンジンmt19937を用いてシード値seedから疑似乱数を生成
    mt19937 gen(seed);

    // ∑の要素数の範囲内で一様分布を生成
    uniform_int_distribution<int> dist(0, alphabets.size() - 1);

    // 一様分布から出力された数値を添字とした要素を返却
    auto alphabet = next(alphabets.begin(), dist(gen));

    return *alphabet;
}

/**
 * @brief 符号割り振りの初期化処理
 *
 * @param vocab vector<string>
 * @param alphabets set<string>
 * @return vector<int>
 */
static vector<int> initZerooneList(
    vector<string> const &vocab,
    set<string> &alphabets)
{
    vector<int> zerooneList;

    for (int i = 0, vocabSize = vocab.size(); i < vocabSize; ++i)
    {
        // メタ文字_が含まれるサブワードに1を付与
        if (vocab[i].find('_') != string::npos)
        {
            zerooneList.push_back(1);
            // アルファベット∑から未削除のメタ文字入サブワードを除外
            alphabets.erase(vocab[i]);
        }
        // End of Sentence( <EOS> )に2を付与
        else if (vocab[i] == "<EOS>")
        {
            zerooneList.push_back(2);
            // アルファベット∑から未削除の<EOS>を除外
            alphabets.erase(vocab[i]);
        }
        // その他の文字には未割当符号3を付与
        else
        {
            zerooneList.push_back(3);
        }
    }

    return zerooneList;
}

/**
 * @brief PairCompressionに基づいたラベルの付与
 *
 * @param vocab vector<string>
 * @param alphabets set<string>
 * @param pref size_t
 * @param prefAddress string
 * @return vector<int>
 */
static vector<int> pairCompression(
    vector<string> const &vocab,
    set<string> &alphabets,
    size_t const &pref,
    string const &prefAddress)
{
    vector<int> zerooneList;
    string startWord;
    string pointWord;
    size_t startWordSeed;
    int vocabSize = vocab.size();

    // 符号割り振りの初期化処理
    zerooneList = initZerooneList(vocab, alphabets);

    // アルファベット∑からランダムに1文字を選択
    startWord = choiceStartAlphabet(alphabets, pref);

    cout << "開始文字 : " << startWord << endl;
    for (const char &c : startWord)
    {
        unsigned int ci = static_cast<int>(c);
        cout << ci << endl;
    }

    // 既存のシード値がない場合はシード値seedをprefファイルに保存
    if (pref == -1)
    {
        ofstream ofs;
        ofs.open(prefAddress, ios::app);
        ofs << seed << endl;
    }

    // 開始文字の符号を0に設定
    for (int i = 0; i < vocabSize; ++i)
    {
        if (vocab[i] == startWord)
        {
            zerooneList[i] = 0;
        }
    }

    // アルファベット∑から開始文字を除外
    alphabets.erase(startWord);

    // 2-gram生成の基準文字（開始文字）を設定
    pointWord = startWord;

    // 全ての文字にラベルが付与されたら終了
    while (alphabets.size())
    {
        cout << "アルファベット∑の残り文字数 : " << alphabets.size() << endl;

        int zeroSigmaCount = 0; /* x∑0 or ∑0xの頻度 */
        int oneSigmaCount = 0;  /* x∑1 or ∑1xの頻度 */
        string targetWord;      /* 基準文字の右隣の文字 */

        // 基準文字の右隣の文字x∈∑となるパターンが存在するかどうか
        bool isFindPattern = false;

        // 基準文字の右隣の文字xを探索
        for (int i = 0; i < vocabSize - 1; ++i)
        {
            if (vocab[i] == pointWord && find(alphabets.begin(), alphabets.end(), vocab[i + 1]) != alphabets.end())
            {
                targetWord = vocab[i + 1];
                isFindPattern = true;

                cout << "右隣の文字 : " << targetWord << endl;
                for (const char &c : targetWord)
                {
                    unsigned int ci = static_cast<int>(c);
                    cout << ci << endl;
                }

                break;
            }
        }

        // パターンが見つかった場合
        if (isFindPattern)
        {
            // x? or ?x となるような2-gramを探索する
            for (int i = 0; i < vocabSize - 1; ++i)
            {
                // x? or ?x となるような2-gramが見つかった場合
                if (vocab[i] == targetWord || vocab[i + 1] == targetWord)
                {
                    // x? の場合
                    if (vocab[i] == targetWord)
                    {
                        if (zerooneList[i + 1] == 0)
                        {
                            zeroSigmaCount++;
                        }
                        if (zerooneList[i + 1] == 1)
                        {
                            oneSigmaCount++;
                        }
                    }
                    // ?x の場合
                    if (vocab[i + 1] == targetWord)
                    {
                        if (zerooneList[i] == 0)
                        {
                            zeroSigmaCount++;
                        }
                        if (zerooneList[i] == 1)
                        {
                            oneSigmaCount++;
                        }
                    }
                }
            }

            // 条件に合わせて対象文字に0 or 1を付与
            for (int i = 0; i < vocabSize; ++i)
            {
                if (vocab[i] == targetWord)
                {
                    if (zeroSigmaCount >= oneSigmaCount)
                    {
                        zerooneList[i] = 1;
                    }
                    else
                    {
                        zerooneList[i] = 0;
                    }
                }
            }

            // アルファベット∑から対象文字を除外
            alphabets.erase(targetWord);

            // 基準文字を対象文字に変更
            pointWord = targetWord;
        }
        // パターンが見つからなかった場合
        else
        {
            cout << "パターンが見つかりませんでした" << endl;

            // ラベルが割り振られていない語彙を先頭から探索してその手前の文字を基準文字に設定
            for (int i = 1; i < vocabSize; ++i)
            {
                if (find(alphabets.begin(), alphabets.end(), vocab[i]) != alphabets.end())
                {
                    pointWord = vocab[i - 1];
                    break;
                }
            }
        }
    }

    return zerooneList;
}

/**
 * @brief "01"になるパターンの位置を返す
 *
 * @param vocab vector<string>
 * @param zerooneList vector<int>
 * @param topk int
 * @return tuple<vector<pair<string, string>>, vector<int>>
 */
static tuple<vector<pair<string, string>>, vector<int>> get01Pairs(
    vector<string> const &vocab,
    vector<int> const &zerooneList,
    int const topk)
{
    // key:ペア, value:ペアの出現頻度
    unordered_map<pair<string, string>, int> pairToFreqMap;
    // key:ペア, value:[vocab中での出現位置(index)]
    unordered_map<pair<string, string>, vector<int>> pairToIndexMap;

    // 文字列の探索
    for (int i = 0, vocabSize = vocab.size(); i < vocabSize - 1; ++i)
    {
        // ラベル列が 10 となる部分を探索
        if (zerooneList[i] == 0 && zerooneList[i + 1] == 1)
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

/**
 * @brief 指定されたインデックスに基づいてペアを結合
 *
 * @param vocab vector<string>
 * @param topkIncludeIndexes vector<int>
 */
static void mergeVocab(
    vector<string> &vocab,
    vector<int> const &topkIncludeIndexes,
    double const dropoutRate)
{
    // シード値から擬似乱数を生成
    mt19937 gen(seed);

    // 疑似乱数から乱数生成のための一様分布を生成
    uniform_real_distribution<> dis(0.0, 1.0);

    // 対象のペアの前の文字に次の文字を結合して, 後の文字を削除
    for (int index : topkIncludeIndexes)
    {
        if (dis(gen) > dropoutRate)
        {
            vocab[index] = vocab[index] + vocab[index + 1];
            vocab[index + 1] = "///";
        }
    }

    // ペアの後の文字を削除
    erase(vocab, "///");
}

/**
 * @brief PairCompression-based LCP-dropout
 *
 * @param text string_view
 * @param prefList vector<size_t>
 * @param prefAddress string
 * @param timeAddress string
 * @param topk int
 * @param vocSize int
 * @param dropoutRate double
 *
 * @return tuple<vector<string>, vector<vector<string>>>
 */
static tuple<vector<string>, vector<vector<string>>> lcpDropout(
    string_view const &text,
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

        // 一度のラベル付与から結合までの実行時間計測の開始
        auto startTime = chrono::high_resolution_clock::now();

        // 文書中の出現文字の集合を取得
        set<string> alphabets(vocab.begin(), vocab.end());
        // vector<string> alphabets(alphabetsSets.begin(), alphabetsSets.end());

        // PairCompressionアルゴリズムに基づいてラベル1or0の付与
        if (prefList.empty())
        {
            zerooneList = pairCompression(vocab, alphabets, -1, prefAddress);
        }
        else
        {
            zerooneList = pairCompression(vocab, alphabets, prefList[lcpLoopCount], prefAddress);
        }

        // ラベル 01 を探索し出現回数を計測
        vector<pair<string, string>> topkIncludePairs;
        vector<int> topkIncludeIndexes;
        tie(topkIncludePairs, topkIncludeIndexes) = get01Pairs(vocab, zerooneList, topk);

        // 01 となるペアを結合
        mergeVocab(vocab, topkIncludeIndexes, dropoutRate);

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

/**
 * @brief LCPの実行
 *
 * @param trainAddress string
 * @param prefAddress string
 * @param vocabAddress string
 * @param outAddress string
 * @param timeAddress string
 * @param topk int
 * @param vocSize int
 * @param dropoutRate double
 *
 * @return unordered_set<string>
 */
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
    string text(it, last);
    // string text;
    // train >> text;
    string_view trainText(text);

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
