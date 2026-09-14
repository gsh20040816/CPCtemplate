#include "../src/compact/odd_cycle_vertices.hpp"
#include "../src/classic/odd_cycle_vertices.hpp"
#include <iostream>
#include <random>
#include <pthread.h>

vector<int> brute(int n, const vector<pair<int, int>> &edges)
{
    vector<vector<bool>> g(n + 1, vector<bool>(n + 1));
    for (auto [u, v] : edges)
        if (u != v)
            g[u][v] = g[v][u] = true;
    vector<int> answer(n + 1), path, used(n + 1);
    for (int start = 1; start <= n; start++)
    {
        path = {start};
        used[start] = 1;
        auto search = [&](auto &&self, int u) -> void
        {
            if (path.size() >= 3 && path.size() % 2 && g[u][start])
                for (int v : path)
                    answer[v] = 1;
            for (int v = start + 1; v <= n; v++)
                if (g[u][v] && !used[v])
                {
                    used[v] = 1;
                    path.push_back(v);
                    self(self, v);
                    path.pop_back();
                    used[v] = 0;
                }
        };
        search(search, start);
        used[start] = 0;
    }
    return answer;
}

void check(int n, const vector<pair<int, int>> &edges)
{
    BiconnectedCore a(n);
    static Biconnected_Graph<9> b;
    b.Init(n);
    for (auto [u, v] : edges)
    {
        a.add(u, v);
        b.Insert(u, v);
    }
    a.run();
    b.Run();
    auto expected = brute(n, edges);
    assert(odd_cycle_vertices(a) == expected);
    assert(Odd_Cycle_Vertices(b) == expected);
    // Edge ownership must not depend on the block emission order.
    reverse(a.blocks.begin(), a.blocks.end());
    reverse(b.blocks.begin(), b.blocks.end());
    assert(odd_cycle_vertices(a) == expected);
    assert(Odd_Cycle_Vertices(b) == expected);
}

void *large(void *)
{
    constexpr int n = 100001;
    static Biconnected_Graph<n> b;
    for (int shape = 0; shape < 3; shape++)
    {
        BiconnectedCore a(n);
        b.Init(n);
        auto add = [&](int u, int v)
        {
            a.add(u, v);
            b.Insert(u, v);
        };
        if (shape == 0)
        {
            add(1, 2);
            add(2, 3);
            add(3, 1);
            for (int u = 4; u <= n; u++)
                add(u - 1, u);
        }
        else if (shape == 1)
            for (int u = 2; u <= n; u++)
                add(1, u);
        else
        {
            for (int u = 2; u <= n; u++)
                add(u - 1, u);
            add(n, 1);
        }
        add(n, n);
        a.run();
        b.Run();
        auto x = odd_cycle_vertices(a);
        auto y = Odd_Cycle_Vertices(b);
        assert(x == y);
        for (int u = 1; u <= n; u++)
            assert(x[u] == (shape == 2 || (shape == 0 && u <= 3)));
    }
    return nullptr;
}

int main()
{
    for (int n = 0; n <= 6; n++)
    {
        vector<pair<int, int>> possible;
        for (int u = 1; u <= n; u++)
            for (int v = u + 1; v <= n; v++)
                possible.push_back({u, v});
        for (int mask = 0; mask < (1 << possible.size()); mask++)
        {
            vector<pair<int, int>> edges;
            for (int i = 0; i < (int)possible.size(); i++)
                if (mask >> i & 1)
                    edges.push_back(possible[i]);
            check(n, edges);
        }
    }
    mt19937 rng(2942);
    for (int t = 0; t < 500; t++)
    {
        int n = rng() % 9 + 1;
        vector<pair<int, int>> edges;
        int m = rng() % 22;
        for (int i = 0; i < m; i++)
            edges.push_back({(int)(rng() % n) + 1, (int)(rng() % n) + 1});
        check(n, edges);
    }
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, 512ULL << 20) == 0);
    pthread_t worker;
    assert(pthread_create(&worker, &attr, large, nullptr) == 0);
    assert(pthread_join(worker, nullptr) == 0);
    pthread_attr_destroy(&attr);
    cout << "Odd-cycle vertices dual exhaustive simple-cycle oracle, multigraphs, reordered blocks and 100001-node chain/star/odd-cycle PASS\n";
}
