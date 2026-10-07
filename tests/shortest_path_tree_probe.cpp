#include "../src/compact/shortest_path_tree.hpp"
#include <bit>
#include <iostream>
#include <random>
#include <set>
#include <stdexcept>
using namespace std;
using I = __int128_t;
long long runs = 0, checks = 0;

void require(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle mismatch");
}

vector<I> distances(int n, const vector<ShortestPathTree::Edge> &e, int s)
{
    vector<I> d(n + 1, ShortestPathTree::inf);
    d[s] = 0;
    for (int step = 1; step < n; step++)
    {
        auto next = d;
        for (auto [u, v, w] : e)
        {
            if (d[u] != ShortestPathTree::inf) next[v] = min(next[v], d[u] + w);
            if (d[v] != ShortestPathTree::inf) next[u] = min(next[u], d[v] + w);
        }
        d = next;
    }
    return d;
}

bool certificate(int n, const vector<ShortestPathTree::Edge> &e, int s,
                 const vector<I> &d, const vector<int> &ids, I &weight)
{
    int reached = 0;
    for (int u = 1; u <= n; u++) reached += d[u] != ShortestPathTree::inf;
    if ((int)ids.size() != reached - 1) return false;
    vector<vector<pair<int, long long>>> g(n + 1);
    set<int> used;
    weight = 0;
    for (int id : ids)
    {
        if (id < 0 || id >= (int)e.size() || !used.insert(id).second) return false;
        auto [u, v, w] = e[id];
        g[u].push_back({v, w});
        g[v].push_back({u, w});
        weight += w;
    }
    vector<I> got(n + 1, ShortestPathTree::inf);
    queue<int> q;
    got[s] = 0;
    q.push(s);
    while (!q.empty())
    {
        int u = q.front();
        q.pop();
        for (auto [v, w] : g[u])
            if (got[v] == ShortestPathTree::inf)
            {
                got[v] = got[u] + w;
                q.push(v);
            }
    }
    return got == d;
}

void check(ShortestPathTree &t, int s)
{
    runs++;
    int n = t.n, m = t.e.size();
    auto d = distances(n, t.e, s);
    int reached = 0;
    for (int u = 1; u <= n; u++) reached += d[u] != ShortestPathTree::inf;
    I optimum = ShortestPathTree::inf;
    for (unsigned mask = 0; mask < (1u << m); mask++)
        if (popcount(mask) == reached - 1)
        {
            vector<int> ids;
            for (int id = 0; id < m; id++) if (mask >> id & 1) ids.push_back(id);
            I w;
            if (certificate(n, t.e, s, d, ids, w)) optimum = min(optimum, w);
        }
    require(t.run(s) == reached && t.valid && t.root == s);
    require(t.dis == d && t.weight == optimum);
    I weight;
    require(certificate(n, t.e, s, d, t.ids, weight) && weight == optimum);
    set<int> chosen(t.ids.begin(), t.ids.end());
    for (int v = 1; v <= n; v++)
    {
        if (d[v] == ShortestPathTree::inf)
        {
            require(t.path(v).empty() && t.pre[v] == -1);
            continue;
        }
        vector<int> path;
        int u = v;
        I sum = 0;
        while (u != s)
        {
            require(path.size() < (size_t)n);
            int id = t.pre[u];
            require(chosen.count(id));
            auto edge = t.e[id];
            require(edge.u == u || edge.v == u);
            path.push_back(id);
            sum += edge.w;
            u = edge.u == u ? edge.v : edge.u;
        }
        reverse(path.begin(), path.end());
        require(t.path(v) == path && sum == d[v]);
    }
}

int main(int argc, char **)
{
    try
    {
        for (int n = 1; n <= 4; n++)
        {
            int total = 1 << (n * (n - 1));
            for (int mask = 0; mask < total; mask++)
            {
                ShortestPathTree t(n);
                int code = mask;
                for (int u = 1; u <= n; u++)
                    for (int v = u + 1; v <= n; v++)
                    {
                        int x = code % 4;
                        code /= 4;
                        if (x) t.add(u, v, x - 1);
                    }
                for (int s = 1; s <= n; s++) check(t, s);
            }
        }
        mt19937 rng(545);
        for (int test = 0; test < 300; test++)
        {
            int n = 1 + rng() % 6;
            ShortestPathTree t(n);
            for (int step = 0; step < 9; step++)
            {
                require(t.add(1 + rng() % n, 1 + rng() % n, rng() % 5) == step);
                require(!t.valid);
                check(t, 1 + rng() % n);
                auto copy = t;
                copy.add(1, n, 0);
                check(copy, n);
                check(t, n);
            }
        }
        ShortestPathTree t(4);
        t.add(1, 2, LLONG_MAX);
        t.add(2, 3, LLONG_MAX);
        t.add(3, 4, LLONG_MAX);
        check(t, 1);
        check(t, 4);
        if (argc == 1)
        {
            int n = 300000;
            ShortestPathTree large(n);
            for (int u = 1; u < n; u++) large.add(u, u + 1, LLONG_MAX);
            require(large.run(n) == n);
            require(large.weight == I(n - 1) * LLONG_MAX);
            require(large.path(1).size() == (size_t)n - 1);
            ShortestPathTree zero(n);
            for (int u = 1; u < n; u++) zero.add(u, u + 1, 0);
            require(zero.run(n) == n && zero.weight == 0);
            require(zero.path(1).size() == (size_t)n - 1);
        }
        cout << "PASS " << runs << " runs " << checks << " checks\n";
    }
    catch (const exception &)
    {
        cout << "ORACLE_REJECT\n";
        return argc == 1 ? 1 : 0;
    }
}
