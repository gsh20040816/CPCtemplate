#include "../src/compact/floyd.hpp"
#include <algorithm>
#include <iostream>
#include <random>
#include <stdexcept>
using namespace std;
using I = __int128_t;
long long runs = 0, checks = 0;

void require(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle mismatch");
}

void check(Floyd &t)
{
    runs++;
    int n = t.n;
    vector<vector<I>> best(n + 1, vector<I>(n + 1, Floyd::inf));
    bool cycle = false;
    // Synchronous Bellman-Ford: at most step edges, no Floyd recurrence.
    for (int s = 1; s <= n; s++)
    {
        vector<I> d(n + 1, Floyd::inf);
        d[s] = 0;
        for (int step = 1; step <= n; step++)
        {
            auto next = d;
            for (auto [u, v, w] : t.e)
                if (d[u] != Floyd::inf) next[v] = min(next[v], d[u] + w);
            if (step == n && d != next) cycle = true;
            d = next;
        }
        best[s] = d;
    }
    bool ok = t.run();
    require(ok == !cycle && t.valid == ok);
    if (cycle) return;
    require(t.dis == best);
    for (int s = 1; s <= n; s++)
        for (int v = 1; v <= n; v++)
        {
            if (best[s][v] == Floyd::inf)
            {
                require(t.path(s, v).empty());
                continue;
            }
            vector<int> ids;
            int u = s;
            I sum = 0;
            while (u != v)
            {
                require(ids.size() < (size_t)n);
                int id = t.nxt[u][v];
                require(0 <= id && id < (int)t.e.size());
                auto edge = t.e[id];
                require(edge.u == u);
                ids.push_back(id);
                sum += edge.w;
                u = edge.v;
            }
            require(sum == best[s][v]);
            require(t.path(s, v) == ids);
        }
}

int main(int argc, char **)
{
    try
    {
        for (int n = 1; n <= 3; n++)
        {
            int total = 1 << (2 * n * n);
            for (int mask = 0; mask < total; mask++)
            {
                Floyd t(n);
                int code = mask;
                for (int u = 1; u <= n; u++)
                    for (int v = 1; v <= n; v++)
                    {
                        int x = code % 4;
                        code /= 4;
                        if (x) t.add(u, v, x - 2);
                    }
                check(t);
                if (mask % 71 == 0) check(t);
            }
        }
        mt19937 rng(1672);
        for (int test = 0; test < 400; test++)
        {
            Floyd t(7);
            for (int step = 0; step < 12; step++)
            {
                int u = 1 + rng() % 7, v = 1 + rng() % 7;
                require(t.add(u, v, (int)(rng() % 25) - 12) == step);
                require(!t.valid);
                check(t);
                Floyd copy = t;
                copy.add(1, 1, -1);
                require(!copy.run());
                check(t);
            }
        }
        Floyd extreme(6);
        extreme.add(1, 2, LLONG_MIN);
        extreme.add(2, 3, LLONG_MIN);
        extreme.add(4, 5, LLONG_MAX);
        extreme.add(5, 6, LLONG_MAX);
        check(extreme);
        if (argc == 1)
        {
            int n = 150;
            Floyd t(n);
            for (int u = n; u > 1; u--) t.add(u, u - 1, LLONG_MIN);
            require(t.run());
            require(t.dis[n][1] == I(n - 1) * LLONG_MIN);
            require(t.path(n, 1).size() == (size_t)n - 1);
            // A late pivot closes a negative cycle, before it can amplify.
            t.add(1, n, LLONG_MAX);
            require(!t.run());
            Floyd dense(120);
            for (int u = 1; u <= 120; u++)
                for (int v = 1; v <= 120; v++)
                    if (u != v) dense.add(u, v, LLONG_MIN);
            require(!dense.run());
        }
        cout << "PASS " << runs << " runs " << checks << " checks\n";
    }
    catch (const exception &)
    {
        cout << "ORACLE_REJECT\n";
        return argc == 1 ? 1 : 0;
    }
}
