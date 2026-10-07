#include <bits/stdc++.h>
#include "../src/compact/spfa.hpp"
using namespace std;
using I = __int128_t;
long long checks = 0, runs = 0;

void require(bool ok)
{
    checks++;
    if (!ok)
    {
        cout << "ORACLE_REJECT\n";
        exit(0);
    }
}

void verify(Spfa &t)
{
    int n = t.n;
    I inf = I(1) << 120;
    vector<vector<I>> f(n + 1, vector<I>(n + 1, inf));
    vector<vector<int>> reach(n + 1, vector<int>(n + 1));
    for (int u = 1; u <= n; u++)
    {
        f[u][u] = 0;
        reach[u][u] = 1;
    }
    for (auto [u, v, w] : t.e)
    {
        f[u][v] = min(f[u][v], I(w));
        reach[u][v] = 1;
    }
    for (int k = 1; k <= n; k++)
        for (int u = 1; u <= n; u++)
            for (int v = 1; v <= n; v++)
            {
                reach[u][v] |= reach[u][k] && reach[k][v];
                if (f[u][k] != inf && f[k][v] != inf)
                    f[u][v] = min(f[u][v], f[u][k] + f[k][v]);
            }
    for (int s = 0; s <= n; s++)
    {
        vector<int> neg(n + 1), exists(n + 1);
        bool any = false;
        for (int v = 1; v <= n; v++)
        {
            exists[v] = s == 0 || reach[s][v];
            for (int k = 1; k <= n; k++)
                neg[v] |= (s == 0 || reach[s][k]) && f[k][k] < 0 && reach[k][v];
            any |= neg[v];
        }
        require(t.run(s) == !any);
        require(t.valid == !any);
        runs++;
        if (any) continue;
        for (int v = 1; v <= n; v++)
        {
            require((t.dis[v] != Spfa::inf) == bool(exists[v]));
            auto path = t.path(v);
            if (!exists[v] || neg[v])
            {
                require(path.empty());
                continue;
            }
            I want = s ? f[s][v] : 0;
            if (!s)
                for (int u = 1; u <= n; u++) want = min(want, f[u][v]);
            require(t.dis[v] == want);
            require(path.size() < (size_t)n);
            if (path.empty())
            {
                require(want == 0 && (s == 0 || v == s));
                continue;
            }
            for (int id : path) require(0 <= id && id < (int)t.e.size());
            int u = t.e[path[0]].u;
            require(s == 0 || s == u);
            vector<int> seen(n + 1);
            seen[u] = 1;
            I sum = 0;
            for (int id : path)
            {
                auto edge = t.e[id];
                require(edge.u == u && !seen[edge.v]);
                seen[edge.v] = 1;
                sum += edge.w;
                u = edge.v;
            }
            require(u == v && sum == want);
        }

    }
}

int main(int argc, char **)
{
    for (int n = 1; n <= 3; n++)
    {
        int ways = 1 << (2 * n * n);
        for (int mask = 0; mask < ways; mask++)
        {
            Spfa t(n);
            int code = mask;
            for (int u = 1; u <= n; u++)
                for (int v = 1; v <= n; v++)
                {
                    int digit = code & 3;
                    code >>= 2;
                    if (digit) t.add(u, v, digit - 2);
                }
            verify(t);
        }
    }
    for (auto edges : vector<vector<tuple<int,int,long long>>>{
        {{1,1,-1},{1,2,LLONG_MAX},{2,3,LLONG_MAX}},
        {{1,2,LLONG_MIN},{2,3,LLONG_MIN}},
        {{1,2,LLONG_MAX},{2,3,LLONG_MAX}},
        {{1,2,LLONG_MIN},{2,1,LLONG_MAX},{2,3,0}},
        {{2,2,LLONG_MIN},{2,3,LLONG_MAX}},
        {{1,2,LLONG_MAX},{1,2,LLONG_MIN},{2,3,LLONG_MAX}},
        {{1,2,LLONG_MAX},{2,1,LLONG_MIN+1},{2,3,0}}})
    {
        Spfa t(3);
        for (auto [u,v,w] : edges) t.add(u,v,w);
        verify(t);
    }
    mt19937 rng(1197);
    for (int test = 0; test < 500; test++)
    {
        int n = 1 + rng() % 8;
        Spfa t(n);
        for (int i = 0; i < 25; i++)
        {
            require(t.add(1 + rng() % n, 1 + rng() % n, (int)(rng() % 21) - 10) == i);
            require(!t.valid);
            verify(t);
        }
        auto copy = t;
        copy.add(1, 1, -100);
        require(!copy.valid && t.e.size() == 25);
        verify(copy);
        verify(t);
    }
    cout << "SMALL " << runs << " runs " << checks << " checks\n";
    if (argc > 1) return 0;
    int n = 2500;
    Spfa chain(n);
    for (int u = n - 1; u >= 1; u--) chain.add(u, u + 1, LLONG_MAX);
    require(chain.run(1));
    require(chain.dis[n] == I(n - 1) * LLONG_MAX);
    require(chain.path(n).size() == (size_t)n - 1);
    chain.add(n, n, -1);
    require(!chain.run(1) && !chain.valid);
    require(!chain.run(0) && !chain.valid);
    Spfa star(n);
    star.add(1, 1, LLONG_MIN);
    for (int u = 2; u <= n; u++) star.add(1, u, LLONG_MAX);
    require(!star.run(1) && !star.valid);
    require(star.run(2) && star.valid);
    require(star.dis[1] == Spfa::inf && star.dis[2] == 0);
    require(!star.run(0) && !star.valid);
    cout << "PASS " << runs << " runs " << checks << " checks\n";
}
