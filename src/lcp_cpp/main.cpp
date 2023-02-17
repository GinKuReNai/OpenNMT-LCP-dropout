#include <iostream>
#include <string>
#include <sys/stat.h>
#include <yaml-cpp/yaml.h>
#include <unordered_set>
#include "lcp.hpp"
#include "lcp_utility.hpp"

using namespace std;

int main(int argc, char *argv[])
{
    // 設定ファイルの読み込み
    YAML::Node config = YAML::LoadFile(argv[1]);

    string trainAddress = config["file"]["train"].as<string>();
    string prefAddress = config["file"]["pref"].as<string>();
    string vocabAddress = config["file"]["vocab"].as<string>();
    string outAddress = config["file"]["out"].as<string>();
    string csvAddress = "";
    string timeAddress = "";

    if (config["file"]["csv"].IsDefined())
    {
        csvAddress = config["file"]["csv"].as<string>();
    }

    if (config["file"]["time"].IsDefined())
    {
        timeAddress = config["file"]["time"].as<string>();
    }

    // ディレクトリの自動生成
    makeDirectory(trainAddress);
    makeDirectory(prefAddress);
    makeDirectory(vocabAddress);
    makeDirectory(outAddress);
    if (csvAddress != "")
    {
        makeDirectory(csvAddress);
    }
    if (timeAddress != "")
    {
        makeDirectory(timeAddress);
    }

    // 全体の語彙サイズ v
    int vocAll = config["param"]["v"].as<int>();
    // 一度の実行における語彙サイズ l
    int vocSize = config["param"]["l"].as<int>();
    // topk
    int topk = config["param"]["k"].as<int>();
    // ドロップアウト率
    double dropoutRate = 0.0;
    if (config["param"]["d"].IsDefined())
    {
        dropoutRate = config["param"]["d"].as<double>();
    }

    // 一度目のLCP実行
    unordered_set<string>
        subwordSet = lcp(trainAddress, prefAddress, vocabAddress, outAddress, timeAddress, topk, vocSize, dropoutRate);
    // LCP結果を出力処理
    outputSegmentationResult(csvAddress, 0, subwordSet.size());
    // 出力する分割パターン数
    int lcpPatternCount = 1;

    // 各実行で生成されたサブワード数が全体の語彙サイズを満たすまでLCPを実行
    while (subwordSet.size() < vocAll)
    {
        // 適用毎に出力ファイル名を変更
        prefAddress = config["file"]["pref"].as<string>() + to_string(lcpPatternCount);
        vocabAddress = config["file"]["vocab"].as<string>() + to_string(lcpPatternCount);
        outAddress = config["file"]["out"].as<string>() + to_string(lcpPatternCount);

        // LCP実行
        unordered_set<string> newSet = lcp(trainAddress, prefAddress, vocabAddress, outAddress, timeAddress, topk, vocSize, dropoutRate);

        // 和集合で全体の語彙に加える
        // 生成したサブワードの重複を取り除くために和集合で演算を行う
        subwordSet.insert(newSet.begin(), newSet.end());

        // LCP結果を出力処理
        outputSegmentationResult(csvAddress, lcpPatternCount, subwordSet.size());

        lcpPatternCount++;
    }
}
