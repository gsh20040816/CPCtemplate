#include <iostream>
#include "../../src/compact/string.hpp"
#include "../../src/compact/sam_queries.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    int multiple;
    long long k;
    cin >> s >> multiple >> k;
    SuffixAutomaton sam;
    for (char c : s) sam.extend(c - 'a');
    SAMLex index(sam, multiple ? sam.counts() : vector<long long>{});
    auto ans = index.kth(k);
    cout << (ans ? *ans : "-1") << '\n';
}
