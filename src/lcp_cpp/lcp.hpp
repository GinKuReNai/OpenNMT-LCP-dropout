#ifndef LCP_INCLUDED
#define LCP_INCLUDED

#include <string>
#include <unordered_set>

using namespace std;

// LCPの実行
unordered_set<string> lcp(
    string const &trainAddress,
    string const &prefAddress,
    string const &vocabAddress,
    string const &outAddress,
    string const &timeAddress,
    int const topk,
    int const vocSize,
    double const dropoutRate);

#endif
