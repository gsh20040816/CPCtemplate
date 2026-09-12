#include "../src/compact/release_bfs.hpp"
#include "../src/classic/release_bfs.hpp"
#include <iostream>
#include <map>
#include <queue>
#include <random>

vector<int> check(const vector<vector<int>> &g, const vector<int> &open, int s)
{
    auto neighbors = [&](int u, auto visit)
    {
        for (int v : g[u])
            visit(v);
    };
    auto a = release_bfs(open, s, neighbors);
    assert(a == Release_Bfs(open, s, neighbors));
    vector<int> d(g.size(), INT_MAX);
    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> q;
    d[s] = open[s];
    q.push({d[s], s});
    while (!q.empty())
    {
        auto [t, u] = q.top();
        q.pop();
        if (t != d[u])
            continue;
        for (int v : g[u])
        {
            int z = max(t + 1, open[v]);
            if (z < d[v])
            {
                d[v] = z;
                q.push({z, v});
            }
        }
    }
    for (int &x : d)
        if (x == INT_MAX)
            x = -1;
    assert(a == d);
    return a;
}

int main()
{
    mt19937 rng(92731);
    for (int trial = 0; trial < 10000; trial++)
    {
        int n = 1 + rng() % 50;
        vector<vector<int>> g(n);
        vector<int> open(n);
        for (int u = 0; u < n; u++)
        {
            open[u] = rng() % 200;
            for (int j = 0; j < n; j++)
                if (rng() % 6 == 0)
                    g[u].push_back(rng() % n);
        }
        check(g, open, rng() % n);
    }
    check({{1, 2}, {}, {3}, {}}, {0, 100, 0, 5}, 0);
    long long cases = 0;
    // Enumerate obstacles and every simple initial snake in a 2 x 3 grid.
    for (int mask = 1; mask < 64; mask++)
    {
        vector<vector<int>> g(6);
        for (int u = 0; u < 6; u++)
            for (int v = 0; v < 6; v++)
                if ((mask >> u & 1) && (mask >> v & 1)
                    && abs(u / 3 - v / 3) + abs(u % 3 - v % 3) == 1)
                    g[u].push_back(v);
        vector<int> body;
        auto enumerate = [&](auto &&self, int u) -> void
        {
            body.push_back(u);
            vector<int> open(6);
            for (int i = 1; i < int(body.size()); i++)
                open[body[i]] = body.size() - i;
            auto expected = check(g, open, body[0]);
            map<vector<int>, int> seen;
            queue<vector<int>> q;
            seen[body] = 0;
            q.push(body);
            vector<int> actual(6, -1);
            while (!q.empty())
            {
                auto b = q.front();
                q.pop();
                int t = seen[b];
                if (actual[b[0]] == -1)
                    actual[b[0]] = t;
                auto push = [&](vector<int> c)
                {
                    if (seen.emplace(c, t + 1).second)
                        q.push(c);
                };
                if (b.size() > 1)
                    push(vector<int>(b.begin(), b.end() - 1));
                for (int v : g[b[0]])
                    if (find(b.begin(), b.end() - 1, v) == b.end() - 1)
                    {
                        vector<int> c{v};
                        c.insert(c.end(), b.begin(), b.end() - 1);
                        push(c);
                    }
            }
            assert(actual == expected);
            cases++;
            for (int v : g[u])
                if (find(body.begin(), body.end(), v) == body.end())
                    self(self, v);
            body.pop_back();
        };
        for (int s = 0; s < 6; s++)
            if (mask >> s & 1)
                enumerate(enumerate, s);
    }
    int side = 3000;
    vector<int> open(side * side);
    auto neighbors = [&](int u, auto visit)
    {
        if (u >= side)
            visit(u - side);
        if (u + side < side * side)
            visit(u + side);
        if (u % side)
            visit(u - 1);
        if (u % side + 1 < side)
            visit(u + 1);
    };
    for (int style = 0; style < 2; style++)
    {
        auto d = style ? Release_Bfs(open, 0, neighbors) : release_bfs(open, 0, neighbors);
        for (int u = 0; u < side * side; u++)
            assert(d[u] == u / side + u % side);
    }
    cout << "Release BFS dual heap oracle, exhaustive tiny snake states and 3000-square implicit grid PASS\n";
    cout << "Snake configurations: " << cases << '\n';
}
