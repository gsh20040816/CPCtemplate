#include "../src/compact/xor_path_sum.hpp"
#include <bits/stdc++.h>
using namespace std;
using i64 = long long;
namespace original
{
#include "fixtures/wida_xor_path/07C.cpp"
}

long long checks = 0;
void require(bool ok)
{
    if (!ok)
        throw runtime_error("xor path oracle mismatch");
    checks++;
}

struct Source
{
    vector<original::Node> t;
    vector<vector<int>> child;
    int root = -1;
    void init(int u)
    {
        for (int v : child[u])
        {
            init(v);
            original::add(&t[u], t[v].tot);
        }
        original::update(&t[u]);
    }
    Source(const vector<int> &p, const vector<int> &a) : t(p.size()), child(p.size())
    {
        for (int i = 0; i < (int)p.size(); i++)
        {
            t[i].val.t = a[i];
            if (p[i] < 0)
                root = i;
            else
            {
                t[i].p = &t[p[i]];
                child[p[i]].push_back(i);
            }
        }
        init(root);
    }
    i64 set(int x, int value)
    {
        original::access(&t[x], value);
        return t[x].tot.ans;
    }
};

i64 brute(const vector<int> &p, const vector<int> &a)
{
    int n = p.size();
    vector<vector<int>> g(n);
    for (int u = 0; u < n; u++)
        if (p[u] >= 0)
        {
            g[u].push_back(p[u]);
            g[p[u]].push_back(u);
        }
    i64 ans = 0;
    for (int s = 0; s < n; s++)
    {
        auto dfs = [&](auto &&self, int u, int fa, int x) -> void
        {
            x ^= a[u];
            if (u >= s)
                ans += x;
            for (int v : g[u])
                if (v != fa)
                    self(self, v, u, x);
        };
        dfs(dfs, s, -1, 0);
    }
    return ans;
}

void inspect(const XorPathSum &g)
{
    for (int u = 1; u < (int)g.t.size(); u++)
    {
        const auto &a = g.t[u];
        for (int v : a.ch)
            if (v)
                require(g.t[v].p == u);
        auto expected = XorPathSum::join(XorPathSum::join(g.t[a.ch[0]].tot, a.val), g.t[a.ch[1]].tot);
        require(expected.path == a.tot.path && expected.sum == a.tot.sum);
        require(expected.up == a.tot.up && expected.down == a.tot.down);
        for (int bit = 0; bit < 27; bit++)
            for (int k = 0; k < 2; k++)
            {
                require(a.cnt[bit][k] >= 0 && a.pairs[bit][k] >= 0);
                require(a.val.up[bit][k] == a.val.down[bit][k]);
            }
    }
}

vector<int> large_parent()
{
    vector<int> p(100001);
    p[0] = -1;
    p[1] = p[50001] = 0;
    for (int i = 2; i <= 50000; i++)
        p[i] = 1;
    for (int i = 50002; i <= 100000; i++)
        p[i] = 50001;
    return p;
}

int main(int argc, char **argv)
{
    if (argc > 1 && string(argv[1]) == "source-wide")
    {
        auto p = large_parent();
        Source s(p, vector<int>(p.size()));
        cout << s.set(0, 1) << '\n';
        return 0;
    }
    try
    {
        mt19937 rng(20261013);
        for (int it = 0; it < 800; it++)
        {
            int n = 1 + rng() % 24;
            vector<int> p(n), a(n), order(n);
            iota(order.begin(), order.end(), 0);
            shuffle(order.begin(), order.end(), rng);
            p[order[0]] = -1;
            for (int i = 1; i < n; i++)
                p[order[i]] = order[rng() % i];
            for (int &x : a)
                x = rng() & ((1 << 27) - 1);
            XorPathSum g(p, a);
            Source source(p, a);
            require(g.sum() == brute(p, a));
            require(source.t[source.root].tot.ans == g.sum());
            for (int q = 0; q < 70; q++)
            {
                int u = rng() % n;
                int v = q % 8 == 0 ? a[u] : rng() & ((1 << 27) - 1);
                a[u] = v;
                i64 want = brute(p, a);
                require(g.set(u, v) == want);
                require(source.set(u, v) == want);
                require(g.sum() == want);
                inspect(g);
                if (q == 35)
                {
                    auto copy = g;
                    a[u] ^= 1;
                    require(copy.set(u, a[u]) == brute(p, a));
                    require(g.sum() == want);
                    a[u] ^= 1;
                }
            }
        }
        {
            auto p = large_parent();
            XorPathSum g(p, vector<int>(p.size()));
            require(g.sum() == 0);
            require(g.set(0, 1) == 2500100001LL);
            require(g.set(0, (1 << 27) - 1) == 2500100001LL * ((1 << 27) - 1));
            require(g.set(0, 0) == 0);
        }
        const int n = 100000, mask = (1 << 27) - 1;
        {
            vector<int> p(n), a(n, mask);
            for (int i = 0; i < n; i++)
                p[i] = i - 1;
            XorPathSum g(p, a);
            i64 odd = 1LL * (n / 2 + 1) * ((n + 1) / 2);
            require(g.sum() == mask * odd);
            for (int x : {0, n / 2, n - 1, 1, n / 3})
            {
                i64 l = x + 1, r = n - x;
                i64 odd_here = ((l + 1) / 2) * ((r + 1) / 2) + (l / 2) * (r / 2);
                require(g.set(x, 0) == mask * (odd + l * r - 2 * odd_here));
                require(g.set(x, mask) == mask * odd);
            }
        }
        {
            vector<int> p(n), a(n, mask);
            p[0] = -1;
            XorPathSum g(p, a);
            i64 odd = n + 1LL * (n - 1) * (n - 2) / 2;
            require(g.sum() == mask * odd);
            require(g.set(0, 0) == 2LL * (n - 1) * mask);
            require(g.set(0, mask) == mask * odd);
        }
        cout << "PASS " << checks << " certificates; 56000 original/core/enumerated updates; 100000-node chain/star; wide branch product\n";
    }
    catch (const exception &e)
    {
        cerr << e.what() << '\n';
        return 1;
    }
}
