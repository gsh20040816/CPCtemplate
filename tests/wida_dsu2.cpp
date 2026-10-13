#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_dsu2/main.cpp"

struct Model {
    vector<int> fa;
    vector<pair<int, int>> edges;
    Model(int n) : fa(n + 1) { iota(fa.begin(), fa.end(), 0); }
    int get(int x) const {
        while (fa[x] != x) x = fa[x];
        return x;
    }
    bool merge(int x, int y) {
        edges.push_back({x, y});
        int a = get(x), b = get(y);
        if (a == b) return false;
        fa[min(a, b)] = max(a, b);
        return true;
    }
    int size(int x) const {
        int r = get(x), c = 0;
        for (int i = 0; i < (int)fa.size(); i++) if (get(i) == r) c++;
        return c;
    }
    int E(int x) const {
        int r = get(x), c = 0;
        for (auto [a, b] : edges) if (get(a) == r || get(b) == r) c++;
        return c;
    }
    bool F(int x) const {
        int r = get(x);
        for (auto [a, b] : edges) if (a == b && get(a) == r) return true;
        return false;
    }
};

int main()
{
    DSU d(5);
    Model m(5);
    vector<pair<int, int>> ops = {{1, 2}, {2, 3}, {1, 3}, {4, 4}, {3, 4}, {1, 2}};
    for (int step = 0; step < (int)ops.size(); step++) {
        auto [x, y] = ops[step];
        bool got = d.merge(x, y);
        bool expect = m.merge(x, y);
        if (got != expect) return 1;
        if (step == 2 && (d.F(1) || d.E(1) != 3 || d.size(1) != 3)) return 1;
    }
    for (int x = 0; x <= 5; x++) {
        if (d.get(x) != m.get(x) || d.size(x) != m.size(x) || d.E(x) != m.E(x) || d.F(x) != m.F(x)) return 1;
    }
    if (!d.F(1) || !d.F(4) || d.F(5) || d.E(1) != 6 || d.size(1) != 4 || d.size(0) != 1) return 1;
    cout << "ok\n";
}
