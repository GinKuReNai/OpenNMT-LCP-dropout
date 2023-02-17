#ifndef LCP_UTILITY_INCLUDED
#define LCP_UTILITY_INCLUDED

#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <list>

using namespace std;

// 連想配列にインデックスを追加
void insertIndex(
    unordered_map<string, list<int>> &mp,
    string const &word,
    int const wordNum);

// join関数
string join(vector<string> const &stringsList, string const &delim);

// 出力データの整形&保存
void outputResults(
    vector<string> const &subwordList,
    vector<vector<string>> const &savePairs,
    string const &vocabAddress,
    string const &outAddress);

// std::chrono::high_resolution_clock::now()の結果を
// std::chrono::time_pointからstd::stringにキャストして返却
size_t generateHighResolutionClock(void);

// 連想配列を降順にソート
vector<pair<pair<string, string>, int>> sortMapByDescOrder(
    unordered_map<pair<string, string>, int> stdmap);

// 連想配列を降順にソート
vector<pair<pair<string, string>, vector<int>>> sortMapByDescOrder(
    unordered_map<pair<string, string>, vector<int>> stdmap);

// ディレクトリの自動生成
void makeDirectory(string const &path);

// サブワード分割処理結果を出力処理
void outputSegmentationResult(
    string const &csvFile,
    int lcpLoopCount,
    int subwordCount);

#endif
