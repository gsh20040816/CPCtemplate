#include "../../src/compact/vertex_removal.hpp"
#include <bits/stdc++.h>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m && n)
    {
        BiconnectedCore g(n);
        int u, v;
        while (cin >> u >> v && u != -1) g.add(u + 1, v + 1);
        g.run();
        auto [before, after] = removal_components(g);
        vector<pair<int, int>> a;
        for (int u = 1; u <= n; u++) a.push_back({-after[u], u - 1});
        sort(a.begin(), a.end());
        for (int i = 0; i < m; i++) cout << a[i].second << ' ' << -a[i].first << '\n';
        cout << '\n';
    }
}
