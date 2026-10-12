#include <bits/stdc++.h>
#include <cassert>
#include "../src/compact/dynamic_peach_tree.hpp"
using namespace std;
using ll = long long;
namespace source
{
using i64 = long long;
constexpr i64 inf = 1LL << 60;
#include "fixtures/wida_peach/07B.cpp"
}

array<ll, 4> slow(int u, const vector<vector<int>> &ch,
                  const vector<ll> &b, const vector<ll> &g, const vector<ll> &h)
{
    array<ll, 4> a{b[u] + h[u] - g[u], h[u], b[u] + h[u], 0};
    for (int v : ch[u])
    {
        auto s = slow(v, ch, b, g, h);
        a[0] += s[0];
        a[1] += min({s[1], s[2], 0LL});
        a[2] += *min_element(s.begin(), s.end());
    }
    return a;
}

void init_source(int u, const vector<vector<int>> &ch, vector<source::Node> &t)
{
    for (int v : ch[u])
    {
        t[v].p = &t[u];
        init_source(v, ch, t);
        auto a = source::get(&t[v]);
        t[u].sumg += a[0];
        t[u].sumh += min({a[1], a[2], 0LL});
        t[u].sumb += *min_element(a.begin(), a.end());
    }
    t[u].update();
    source::pull(&t[u]);
}

int main()
{
    mt19937 rng(1942);
    long long checks = 0;
    for (int trial = 0; trial < 1000; trial++)
    {
        int n = 1 + rng() % 60;
        vector<int> perm(n), parent(n, -1);
        iota(perm.begin(), perm.end(), 0);
        shuffle(perm.begin(), perm.end(), rng);
        vector<vector<int>> ch(n);
        for (int i = 1; i < n; i++)
        {
            parent[perm[i]] = perm[rng() % i];
            ch[parent[perm[i]]].push_back(perm[i]);
        }
        vector<ll> b(n), g(n), h(n);
        vector<source::Node> original(n);
        for (int i = 0; i < n; i++)
        {
            b[i] = rng() % 100;
            original[i].b = b[i];
        }
        init_source(perm[0], ch, original);
        DynamicPeachTree tree(parent, b);
        assert(tree.ans == slow(perm[0], ch, b, g, h));
        for (int q = 0; q < 150; q++)
        {
            int x = rng() % n, type = 1 + rng() % 2;
            ll v = rng() % 1000;
            if (type == 1)
            {
                g[x] += v;
                original[x].g += v;
            }
            else
            {
                h[x] += v;
                original[x].h += v;
            }
            source::access(&original[x]);
            auto truth = slow(perm[0], ch, b, g, h);
            bool expected = truth[0] == *min_element(truth.begin(), truth.end());
            assert(tree.add(type, x, v) == expected);
            assert(tree.ans == truth);
            assert(source::get(&original[x]) == truth);
            auto copy = tree;
            assert(copy.add(1, x, 0) == expected);
            assert(copy.ans == truth);
            checks += 5;
        }
    }
    for (bool star : {false, true})
    {
        int n = 200000;
        vector<int> p(n, -1);
        vector<ll> b(n, 1000000);
        for (int i = 1; i < n; i++)
            p[i] = star ? 0 : i - 1;
        DynamicPeachTree tree(p, b);
        assert(!tree.healthy());
        assert(tree.add(1, 0, 200000000000LL));
        assert(!tree.add(2, n - 1, 1));
        assert(tree.add(1, n - 1, 1));
        assert(tree.add(1, 0, 999599999999998LL));
        assert(tree.budget == 1000000000000000LL);
        checks += 6;
    }
    cout << checks << " state/source/copy/large-tree checks passed\n";
}
