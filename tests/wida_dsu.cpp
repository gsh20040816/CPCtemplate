#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_dsu/main.cpp"

static int naive_root(vector<int> fa, int x)
{
    while (fa[x] != x) x = fa[x];
    return x;
}

int main()
{
    DSU d(5);
    vector<int> fa(6);
    iota(fa.begin(), fa.end(), 0);
    vector<pair<int, int>> ops = {{1, 2}, {2, 3}, {4, 5}, {3, 5}, {1, 5}};
    for (auto [x, y] : ops) {
        bool first = naive_root(fa, x) != naive_root(fa, y);
        if (d.merge(x, y) != first) return 1;
        int a = naive_root(fa, x), b = naive_root(fa, y);
        if (a != b) fa[min(a, b)] = max(a, b);
    }
    for (int x = 0; x <= 5; x++) {
        if (d.get(x) != naive_root(fa, x)) return 1;
        int cnt = 0;
        for (int y = 0; y <= 5; y++) if (naive_root(fa, y) == naive_root(fa, x)) cnt++;
        if (d.size(x) != cnt || d.same(x, x) != 1) return 1;
    }
    if (d.same(0, 1) || !d.same(1, 4) || d.size(1) != 5 || d.size(0) != 1) return 1;
    DSU one(0);
    cout << one.same(0, 0) << ' ' << one.size(0) << '\n';
}
