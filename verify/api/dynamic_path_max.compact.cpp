#include <bits/stdc++.h>
#include "../../src/compact/dynamic_path_max.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    while (cin >> n)
    {
        vector<pair<int, int>> edges(n - 1);
        for (auto &[x, y] : edges)
            cin >> x >> y;
        vector<long long> v(n);
        for (auto &x : v)
            cin >> x;
        DynamicPathMax t(v);
        for (auto [x, y] : edges)
            t.link(x, y);
        int q;
        cin >> q;
        while (q--)
        {
            int op, x, y;
            long long w = 0;
            cin >> op;
            if (op == 3)
                cin >> w;
            cin >> x >> y;
            bool ok = true;
            if (op == 1)
                ok = t.link(x, y);
            else if (op == 2)
                ok = t.cut_parent(x, y);
            else if (op == 3)
                ok = t.add(x, y, w);
            else
            {
                auto ans = t.query(x, y);
                cout << (ans ? *ans : -1) << '\n';
            }
            if (!ok)
                cout << -1 << '\n';
        }
        cout << '\n';
    }
    return 0;
}
