#include "../../src/compact/ac_shortest.hpp"
#include <iostream>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    AhoCorasick ac;
    vector<pair<int, int>> ends;
    while (n--)
    {
        string s;
        cin >> s;
        ends.push_back({ac.add(s), (int)s.size()});
    }
    ac.build();
    auto len = ac_shortest(ac, ends);
    string s;
    cin >> s;
    int u = 0;
    for (char c : s)
    {
        u = ac.a[u].go[c - 'a'];
        cout << (len[u] == INT_MAX ? 0 : len[u]) << ' ';
    }
    cout << '\n';
}
