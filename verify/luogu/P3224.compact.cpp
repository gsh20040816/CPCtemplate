#include <bits/stdc++.h>
#include "../../src/compact/merge_splay.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    MergeSplay t(a);
    while (m--)
    {
        int u, v;
        cin >> u >> v;
        t.merge(u - 1, v - 1);
    }
    int q;
    cin >> q;
    while (q--)
    {
        char op;
        int x, y;
        cin >> op >> x >> y;
        if (op == 'B') t.merge(x - 1, y - 1);
        else
        {
            auto id = t.kth(x - 1, y);
            cout << (id ? *id + 1 : -1) << '\n';
        }
    }
}
