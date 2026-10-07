#include "../src/compact/dag_longest.hpp"
#include <functional>
#include <iostream>
#include <numeric>
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

void check(DagLongest &t, int s)
{
    runs++;
    int n = t.n;
    vector<vector<int>> g(n + 1);
    for (int i = 0; i < (int)t.e.size(); i++) g[t.e[i].u].push_back(i);
    vector<int> color(n + 1);
    bool cycle = false;
    function<void(int)> visit = [&](int u)
    {
        color[u] = 1;
        for (int id : g[u])
        {
            int v = t.e[id].v;
            if (color[v] == 1) cycle = true;
            if (!color[v]) visit(v);
        }
        color[u] = 2;
    };
    for (int u = 1; u <= n; u++) if (!color[u]) visit(u);
    bool ok = t.run(s);
    require(ok == !cycle && t.valid == ok);
    if (cycle) return;
    vector<I> best(n + 1, -DagLongest::inf);
    function<void(int, I)> walk = [&](int u, I w)
    {
        best[u] = max(best[u], w);
        for (int id : g[u]) walk(t.e[id].v, w + t.e[id].w);
    };
    for (int u = 1; u <= n; u++) if (!s || u == s) walk(u, 0);
    require(t.dis == best);
    require((int)t.ord.size() == n);
    vector<int> pos(n + 1, -1);
    for (int i = 0; i < n; i++)
    {
        int u = t.ord[i];
        require(1 <= u && u <= n && pos[u] == -1);
        pos[u] = i;
    }
    for (auto e : t.e) require(pos[e.u] < pos[e.v]);
    for (int v = 1; v <= n; v++)
    {
        vector<int> ids;
        int u = v;
        I sum = 0;
        while (t.pre[u] != -1)
        {
            require(ids.size() < (size_t)n);
            int id = t.pre[u];
            require(0 <= id && id < (int)t.e.size());
            auto e = t.e[id];
            require(e.v == u);
            ids.push_back(id);
            sum += e.w;
            u = e.u;
        }
        reverse(ids.begin(), ids.end());
        require(t.path(v) == ids);
        if (best[v] == -DagLongest::inf) require(ids.empty());
        else require(sum == best[v] && (!s || u == s));
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
                DagLongest t(n);
                int code = mask;
                for (int u = 1; u <= n; u++)
                    for (int v = 1; v <= n; v++)
                    {
                        int x = code % 4;
                        code /= 4;
                        if (x) t.add(u, v, x - 2);
                    }
                for (int s = 0; s <= n; s++) check(t, s);
            }
        }
        vector<int> p = {1, 2, 3, 4};
        do
        {
            for (int mask = 0; mask < 4096; mask++)
            {
                DagLongest t(4);
                int code = mask;
                for (int i = 0; i < 4; i++)
                    for (int j = i + 1; j < 4; j++)
                    {
                        int x = code % 4;
                        code /= 4;
                        if (x) t.add(p[i], p[j], x - 2);
                    }
                for (int s = 0; s <= 4; s++) check(t, s);
            }
        } while (next_permutation(p.begin(), p.end()));
        mt19937 rng(1807);
        for (int test = 0; test < 300; test++)
        {
            DagLongest t(6);
            for (int step = 0; step < 12; step++)
            {
                int u = 1 + rng() % 6, v = 1 + rng() % 6;
                require(t.add(u, v, (int)(rng() % 21) - 10) == step);
                require(!t.valid);
                check(t, step % 7);
                DagLongest copy = t;
                copy.add(1, 1, 0);
                require(!copy.run(0));
                check(t, (step + 1) % 7);
            }
        }
        DagLongest extreme(6);
        extreme.add(1, 2, LLONG_MIN);
        extreme.add(2, 3, LLONG_MIN);
        extreme.add(4, 5, LLONG_MAX);
        extreme.add(5, 6, LLONG_MAX);
        for (int s = 0; s <= 6; s++) check(extreme, s);
        if (argc == 1)
        {
            int n = 100000;
            DagLongest t(n);
            for (int u = n; u > 1; u--) t.add(u, u - 1, LLONG_MIN);
            require(t.run(n));
            require(t.dis[1] == I(n - 1) * LLONG_MIN);
            require(t.path(1).size() == (size_t)n - 1);
            require(t.run(1) && t.dis[n] == -DagLongest::inf);
            require(t.run(0) && t.dis[1] == 0 && t.path(1).empty());
        }
        cout << "PASS " << runs << " runs " << checks << " checks\n";
    }
    catch (const exception &)
    {
        cout << "ORACLE_REJECT\n";
        return argc == 1 ? 1 : 0;
    }
}
