#include <bits/stdc++.h>
#include "../../src/compact/dag_longest.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, s;
    cin >> n >> m >> s;
    DagLongest t(n);
    while (m--)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        t.add(u, v, w);
    }
    if (!t.run(s))
    {
        cout << "CYCLIC\n";
        return 0;
    }
    auto print = [](__int128 x)
    {
        if (x < 0)
        {
            cout << '-';
            x = -x;
        }
        string a;
        do
        {
            a += char('0' + x % 10);
            x /= 10;
        } while (x);
        reverse(a.begin(), a.end());
        cout << a;
    };
    for (int u = 1; u <= n; u++)
    {
        if (t.dis[u] == -DagLongest::inf) cout << "INF\n";
        else
        {
            auto path = t.path(u);
            print(t.dis[u]);
            cout << ' ' << path.size();
            for (int id : path) cout << ' ' << id;
            cout << '\n';
        }
    }
}
