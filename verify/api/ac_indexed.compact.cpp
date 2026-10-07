#include "../../src/compact/string.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q, offset;
    cin >> n >> q >> offset;
    AhoCorasick ac;
    vector<int> end(n);
    for (int &u : end)
    {
        int m;
        cin >> m;
        vector<int> s(m);
        for (int &x : s) cin >> x;
        u = ac.add(s, offset);
    }
    ac.build();
    for (int u : end) cout << ac.a[u].len << ' ';
    cout << '\n';
    while (q--)
    {
        int m;
        cin >> m;
        vector<int> s(m);
        for (int &x : s) cin >> x;
        auto cnt = ac.count(s, offset);
        for (int u : end) cout << cnt[u] << ' ';
        cout << '\n';
    }
}
