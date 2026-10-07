#include <bits/stdc++.h>
#include "../../src/compact/dag_longest.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    DagLongest t(n);
    while (m--)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        t.add(u, v, w);
    }
    t.run(1);
    if (t.dis[n] == -DagLongest::inf) cout << -1 << '\n';
    else cout << (long long)t.dis[n] << '\n';
}
