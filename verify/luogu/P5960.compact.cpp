#include <bits/stdc++.h>
#include "../../src/compact/spfa.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    Spfa t(n);
    while (m--)
    {
        int u, v, w;
        cin >> u >> v >> w;
        t.add(v, u, w);
    }
    if (!t.run(0)) cout << "NO\n";
    else
        for (int u = 1; u <= n; u++)
            cout << (long long)t.dis[u] << " \n"[u == n];
}
