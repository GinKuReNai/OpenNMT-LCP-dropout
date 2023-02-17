/**
 * @file lcp_utility.cpp
 * @author Akito Koga (koga.akito893@mail.kyutech.jp)
 * @brief lcpの処理をサポートする自作ユーティリティ関数群
 * @date 2023-01-29
 *
 * @copyright Copyright (c) 2023
 */

#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <regex>
#include <chrono>
#include <filesystem>
#include <numeric>
#include <unordered_map>
#include <list>

using namespace std;

// 連想配列にインデックスを追加
void insertIndex(
    unordered_map<string, list<int>> &mp,
    string const &word,
    int const wordNum)
{
    // 既出の文字の場合, 連想配列のインデックスの配列の末尾に追加する
    if (mp.find(word) != mp.end())
    {
        mp[word].push_back(wordNum);
    }
    // 未出現の文字の場合, 連想配列にインデックスの配列を登録する
    else
    {
        mp[word] = {wordNum};
    }
}

/**
 * @brief 区切り文字delimに基づいて配列の各文字列を結合
 *
 * @param stringsList vector<string>
 * @param delim string
 *
 * @return string
 */
string join(vector<string> const &stringsList, string const &delim)
{
    string joinedStrings;
    for_each(stringsList.begin(), stringsList.end() - 1, [&joinedStrings, &delim](const string &str)
             { joinedStrings += (str + delim); });
    joinedStrings += stringsList.back();

    return joinedStrings;
}

/**
 * @brief 出力データの整形&保存
 *
 * @param subwordList vector<string>
 * @param mergedPairs vector<vector<string>>
 * @param vocabAddress string
 * @param outAddress string
 */
void outputResults(
    vector<string> const &subwordList,
    vector<vector<string>> const &mergedPairs,
    string const &vocabAddress,
    string const &outAddress)
{
    // 空白区切りでサブワードを結合
    string delim = " ";
    string subwordText = join(subwordList, delim);

    // <EOS>を改行に置換
    subwordText = regex_replace(subwordText, regex("<EOS>"), "\n");

    // 変換済み文章を出力
    ofstream outFile(outAddress);
    if (!outFile)
    {
        cerr << "出力ファイルが見つかりません." << endl;
        exit(1);
    }
    // UTF-8に変換してファイルに出力
    outFile << subwordText << endl;

    // 結合した2-gramをvocabファイルに保存
    ofstream vocab(vocabAddress);
    if (!vocab)
    {
        cerr << "vocabファイルが見つかりません." << endl;
        exit(1);
    }
    for (vector<string> pairList : mergedPairs)
    {
        // UTF-8に変換してファイルに出力
        vocab << join(pairList, "");
        vocab << "@@@" << endl;
    }
}

/**
 * @brief シード値となる現在時刻を出力
 *
 * @return size_t
 */
size_t generateHighResolutionClock(void)
{
    auto now = chrono::high_resolution_clock::now();
    auto duration = now.time_since_epoch();

    size_t epochValue = duration.count();
    
    return epochValue;
}

/**
 * @brief 降順にソートする比較関数(int)
 *
 * @param a pair<pair<string, string>, int>
 * @param b pair<pair<string, string>, int>
 *
 * @return true
 * @return false
 */
static bool compareByValueForDescForInt(
    const pair<pair<string, string>, int> &a,
    const pair<pair<string, string>, int> &b)
{
    return a.second > b.second;
}

/**
 * @brief 降順にソートする比較関数(vector)
 *
 * @param a pair<pair<string, string>, vector<int>>
 * @param b pair<pair<string, string>, vector<int>>
 *
 * @return true
 * @return false
 */
static bool compareByValueForDescForVector(
    const pair<pair<string, string>, vector<int>> &a,
    const pair<pair<string, string>, vector<int>> &b)
{
    return a.second.size() > b.second.size();
}


/**
 * @brief 連想配列を降順にソート(int)
 *
 * @param stdmap unordered_map<pair<string, string>, int>>
 * @return vector<pair<pair<string, string>, int>>
 */
vector<pair<pair<string, string>, int>> sortMapByDescOrder(
    unordered_map<pair<string, string>, int> stdmap)
{
    vector<pair<pair<string, string>, int>> orderedMap(stdmap.begin(), stdmap.end());
    sort(orderedMap.begin(), orderedMap.end(), compareByValueForDescForInt);

    return orderedMap;
}

/**
 * @brief 連想配列を降順にソート(vector)
 *
 * @param stdmap unordered_map<pair<string, string>, vector<int>>>
 * @return vector<pair<pair<string, string>, int>>
 */
vector<pair<pair<string, string>, vector<int>>> sortMapByDescOrder(
    unordered_map<pair<string, string>, vector<int>> stdmap)
{
    vector<pair<pair<string, string>, vector<int>>> orderedMap(stdmap.begin(), stdmap.end());
    sort(orderedMap.begin(), orderedMap.end(), compareByValueForDescForVector);

    return orderedMap;
}

/**
 * @brief ディレクトリの自動生成
 *
 * @param path string
 */
void makeDirectory(string const &path)
{
    regex regex("(.*)/([^/]+)$");
    smatch match;
    string directory = "";

    // パスをディレクトリとファイルに分離
    if (regex_search(path, match, regex))
    {
        directory = match[1];
    }

    // ディレクトリを生成
    filesystem::create_directories(directory);
}

// 合計サブワード数を標準出力
/**
 * @brief 合計サブワード数を標準出力
 *
 * @param subwordCount int
 */
static void outNumOfSubword(int subwordCount)
{
    cout << "===============" << endl;
    cout << "合計サブワード数 : " << subwordCount << endl;
    cout << "===============" << endl;
}

/**
 * @brief CSVファイルの生成
 *
 * @param csvFile string
 * @param param pair<int, int>
 */
static void outputCsv(string const &csvFile, pair<int, int> const &param)
{
    ofstream csv;
    csv.open(csvFile, ios::app);
    csv << param.first << "," << param.second << endl;
}

/**
 * @brief サブワード分割処理結果を出力処理
 *
 * @param csvFile string
 * @param lcpLoopCount int
 * @param subwordCount int
 */
void outputSegmentationResult(
    string const &csvFile,
    int lcpLoopCount,
    int subwordCount)
{
    // 合計サブワード数を標準出力
    outNumOfSubword(subwordCount);

    // CSVファイルに合計サブワード数を出力
    if (csvFile != "")
    {
        pair<int, int> param = {lcpLoopCount, subwordCount};
        outputCsv(csvFile, param);
    }
}
