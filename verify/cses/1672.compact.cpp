#include <bits/stdc++.h>
#include "../../src/compact/floyd.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, q;
    cin >> n >> m >> q;
    Floyd t(n);
    while (m--)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        t.add(u, v, w);
        t.add(v, u, w);
    }
    t.run();
    while (q--)
    {
        int u, v;
        cin >> u >> v;
        if (t.dis[u][v] == Floyd::inf) cout << -1 << '\n';
        else cout << (long long)t.dis[u][v] << '\n';
    }
}
