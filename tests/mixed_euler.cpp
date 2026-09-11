#include "../src/compact/mixed_euler.hpp"
#include "../src/classic/mixed_euler.hpp"
#include "../src/compact/directed_euler.hpp"
#include <iostream>
#include <random>
#include <pthread.h>

bool valid(int n, const vector<pair<int, int>> &edges, int start, int finish, bool any)
{
    vector<vector<int>> g(n + 1);
    vector<int> balance(n + 1), degree(n + 1);
    for (auto [u, v] : edges)
    {
        g[u].push_back(v);
        g[v].push_back(u);
        degree[u]++;
        degree[v]++;
        balance[u]++;
        balance[v]--;
    }
    if (!edges.empty())
    {
        vector<int> seen(n + 1), queue{edges[0].first};
        seen[queue[0]] = 1;
        for (int i = 0; i < (int)queue.size(); i++)
            for (int v : g[queue[i]])
                if (!seen[v])
                {
                    seen[v] = 1;
                    queue.push_back(v);
                }
        for (int u = 1; u <= n; u++)
            if (degree[u] && !seen[u])
                return false;
        if (start && (!degree[start] || !degree[finish]))
            return false;
    }
    if (any)
    {
        int positive = 0, negative = 0;
        for (int u = 1; u <= n; u++)
        {
            if (balance[u] == 1)
                positive++;
            else if (balance[u] == -1)
                negative++;
            else if (balance[u])
                return false;
        }
        return positive == negative && positive <= 1;
    }
    for (int u = 1; u <= n; u++)
        if (balance[u] != (u == start) - (u == finish))
            return false;
    return true;
}

bool brute(int n, const vector<array<int, 3>> &edges, int start, int finish, bool any)
{
    int count = 0;
    for (auto edge : edges)
        count += edge[2] == 0;
    for (int mask = 0; mask < (1 << count); mask++)
    {
        vector<pair<int, int>> direction;
        int k = 0;
        for (auto [u, v, type] : edges)
        {
            if (!type && (mask >> k++ & 1))
                swap(u, v);
            direction.push_back({u, v});
        }
        if (valid(n, direction, start, finish, any))
            return true;
    }
    return false;
}

void certificate(int n, const vector<array<int, 3>> &edges,
                 const vector<pair<int, int>> &direction, int start, int finish, bool any)
{
    assert(direction.size() == edges.size());
    assert(valid(n, direction, start, finish, any));
    DirectedEuler trail(n);
    for (int i = 0; i < (int)edges.size(); i++)
    {
        auto [u, v, type] = edges[i];
        assert(direction[i] == make_pair(u, v) || (!type && direction[i] == make_pair(v, u)));
        trail.add(direction[i].first, direction[i].second);
    }
    assert(trail.run(start, false));
    if (!any)
    {
        if (start)
            assert(trail.vertices.front() == start && trail.vertices.back() == finish);
        else
            assert(trail.vertices.front() == trail.vertices.back());
    }
    vector<int> used(edges.size());
    for (int i = 0; i < (int)edges.size(); i++)
    {
        int id = trail.edge_ids[i];
        assert(0 <= id && id < (int)edges.size() && !used[id]);
        used[id] = 1;
        assert(direction[id] == make_pair(trail.vertices[i], trail.vertices[i + 1]));
    }
}

void check(int n, const vector<array<int, 3>> &edges)
{
    static Network_Flow<8, 40> flow;
    for (int s = 0; s <= n; s++)
        for (int t = s ? 1 : 0; t <= (s ? n : 0); t++)
        {
            bool expected = brute(n, edges, s, t, false);
            auto a = mixed_euler_orientation(n, edges, s, t);
            auto b = Mixed_Euler_Orientation(n, edges, flow, s, t);
            assert(a.has_value() == expected && b.has_value() == expected);
            if (a)
                certificate(n, edges, *a, s, t, false);
            if (b)
                certificate(n, edges, *b, s, t, false);
        }
    bool expected = brute(n, edges, 0, 0, true);
    auto a = mixed_euler_trail(n, edges);
    auto b = Mixed_Euler_Trail(n, edges, flow);
    assert(a.has_value() == expected && b.has_value() == expected);
    if (a)
        certificate(n, edges, *a, 0, 0, true);
    if (b)
        certificate(n, edges, *b, 0, 0, true);
}

void *large(void *)
{
    constexpr int n = 100000;
    vector<array<int, 3>> edges;
    for (int u = 1; u < n; u++)
    {
        edges.push_back({u, u + 1, 1});
        edges.push_back({u, u + 1, 0});
    }
    static Network_Flow<n + 2, 300000> flow;
    auto a = mixed_euler_orientation(n, edges);
    auto b = Mixed_Euler_Orientation(n, edges, flow);
    assert(a && b);
    for (int i = 0; i < (int)edges.size(); i++)
    {
        auto [u, v, type] = edges[i];
        if (!type)
            swap(u, v);
        assert((*a)[i] == make_pair(u, v) && (*b)[i] == make_pair(u, v));
    }
    certificate(n, edges, *a, 0, 0, false);
    certificate(n, edges, *b, 0, 0, false);
    return nullptr;
}

int main()
{
    vector<array<int, 3>> options;
    for (int u = 1; u <= 2; u++)
        for (int v = 1; v <= 2; v++)
        {
            options.push_back({u, v, 1});
            if (u <= v)
                options.push_back({u, v, 0});
        }
    vector<array<int, 3>> edges;
    auto enumerate = [&](auto &&self, int first) -> void
    {
        check(2, edges);
        if (edges.size() == 4)
            return;
        for (int i = first; i < (int)options.size(); i++)
        {
            edges.push_back(options[i]);
            self(self, i);
            edges.pop_back();
        }
    };
    enumerate(enumerate, 0);
    mt19937 rng(1637);
    for (int test = 0; test < 400; test++)
    {
        int n = rng() % 6 + 1;
        vector<array<int, 3>> edges;
        int m = rng() % 8;
        for (int i = 0; i < m; i++)
            edges.push_back({(int)(rng() % n) + 1, (int)(rng() % n) + 1, (int)(rng() % 2)});
        check(n, edges);
    }
    check(3, {{1, 2, 0}, {1, 2, 1}});
    check(3, {{2, 1, 1}});
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, 512ULL << 20) == 0);
    pthread_t worker;
    assert(pthread_create(&worker, &attr, large, nullptr) == 0);
    assert(pthread_join(worker, nullptr) == 0);
    pthread_attr_destroy(&attr);
    cout << "Mixed Euler dual exhaustive orientations, fixed/free endpoints, loops, isolated vertices, full trail certificates and 100000-node flow chain PASS\n";
}
