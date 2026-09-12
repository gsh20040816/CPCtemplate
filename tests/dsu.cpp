#include "../src/compact/data_structure.hpp"
#include <iostream>
#include <random>

int main()
{
    mt19937 rng(2);
    dsu e(0);
    assert(e.groups().empty());
    for (int n = 1; n <= 35; n++)
    {
        dsu d(n);
        vector<int> c(n);
        iota(c.begin(), c.end(), 0);
        for (int t = 0; t < 300; t++)
        {
            int x = rng() % n, y = rng() % n;
            int rx = d.find(x), ry = d.find(y);
            bool want = c[x] != c[y];
            assert(d.merge(x, y) == want);
            if (want)
            {
                int old = c[y], cur = c[x];
                for (int &v : c)
                    if (v == old) v = cur;
                assert(d.find(y) == rx && d.fa[ry] == rx);
            }
            for (int i = 0; i < n; i++)
            {
                assert(d.size(i) == count(c.begin(), c.end(), c[i]));
                for (int j = 0; j < n; j++)
                    assert(d.same(i, j) == (c[i] == c[j]));
            }
            auto g = d.groups();
            vector<int> seen(n);
            int last = -1;
            for (auto &v : g)
            {
                assert(!v.empty() && is_sorted(v.begin(), v.end()));
                int r = d.find(v[0]);
                assert(r > last);
                last = r;
                assert(int(v.size()) == d.size(r));
                for (int u : v)
                {
                    assert(!seen[u]++ && d.find(u) == r);
                }
            }
            for (int v : seen) assert(v == 1);
        }
    }
    int n = 500000;
    dsu d(n);
    for (int i = 1; i < n; i++) assert(d.merge(i, i - 1));
    // Adversarial linking forms a long path before the first query from zero.
    assert(d.fa[0] == 1 && d.find(0) == n - 1);
    assert(d.size(0) == n && !d.merge(0, n - 1));
    auto g = d.groups();
    assert(g.size() == 1 && int(g[0].size()) == n);
    for (int i = 0; i < n; i++) assert(g[0][i] == i);
    cout << "User dsu label oracle, root direction, same/size/groups and 500000 unbalanced chain PASS\n";
}
