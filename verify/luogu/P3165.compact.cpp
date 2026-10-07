#include <bits/stdc++.h>
#include "../../src/compact/sequence_splay.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<int> a(n), id(n);
    for (auto &x : a) cin >> x;
    iota(id.begin(), id.end(), 0);
    sort(id.begin(), id.end(), [&](int u, int v)
    {
        return pair{a[u], u} < pair{a[v], v};
    });
    SequenceSplay t(n);
    for (int i = 0; i < n; i++)
    {
        int p = t.pos(id[i]);
        cout << p + 1 << (i + 1 == n ? '\n' : ' ');
        t.reverse(i, p + 1);
    }
}
