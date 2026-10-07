#include "../../src/compact/string.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    AhoCorasick ac;
    vector<int> end(n);
    for (int &u : end)
    {
        string s;
        cin >> s;
        u = ac.add(s);
    }
    ac.build();
    string t;
    cin >> t;
    auto cnt = ac.count(t);
    int ans = 0;
    for (int u : end) ans += cnt[u] > 0;
    cout << ans << '\n';
}
