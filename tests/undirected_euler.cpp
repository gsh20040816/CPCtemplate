#include "../src/compact/undirected_euler.hpp"
#include "../src/classic/undirected_euler.hpp"
#include <iostream>
#include <random>
#include <optional>
#include <pthread.h>

optional<vector<int>> brute(int n, const vector<pair<int, int>> &edges, int start)
{
    optional<vector<int>> best;
    vector<int> path;
    auto search = [&](auto &&self, int u, int mask) -> void
    {
        if (mask == (1 << edges.size()) - 1)
        {
            if (!best || path < *best)
                best = path;
            return;
        }
        for (int i = 0; i < (int)edges.size(); i++)
            if (!(mask >> i & 1) && (edges[i].first == u || edges[i].second == u))
            {
                int v = edges[i].first ^ edges[i].second ^ u;
                path.push_back(v);
                self(self, v, mask | (1 << i));
                path.pop_back();
            }
    };
    for (int u = 1; u <= n; u++)
        if (!start || start == u)
        {
            path = {u};
            search(search, u, 0);
        }
    return best;
}

void certificate(const vector<pair<int, int>> &edges, const vector<int> &vertices,
                 const vector<int> &ids)
{
    assert(ids.size() == edges.size() && vertices.size() == edges.size() + 1);
    vector<int> seen(edges.size());
    for (int i = 0; i < (int)ids.size(); i++)
    {
        int id = ids[i];
        assert(0 <= id && id < (int)edges.size() && !seen[id]);
        seen[id] = 1;
        assert(edges[id] == make_pair(vertices[i], vertices[i + 1]) ||
               edges[id] == make_pair(vertices[i + 1], vertices[i]));
    }
}

void check(int n, const vector<pair<int, int>> &edges)
{
    UndirectedEuler a(n);
    static Undirected_Euler<6> b;
    b.Init(n);
    for (auto [u, v] : edges)
        assert(a.add(u, v) == b.Insert(u, v));
    for (int start = 0; start <= n; start++)
    {
        auto expected = brute(n, edges, start);
        for (bool lex : {false, true, false, true})
        {
            bool x = a.run(start, lex), y = b.Run(start, lex);
            assert(x == expected.has_value() && y == x);
            if (!x)
            {
                assert(a.vertices.empty() && a.edge_ids.empty());
                assert(b.vertices.empty() && b.edge_ids.empty());
                continue;
            }
            certificate(edges, a.vertices, a.edge_ids);
            certificate(edges, b.vertices, b.edge_ids);
            if (lex)
                assert(a.vertices == *expected && b.vertices == *expected);
        }
    }
    a.add(1, 1);
    b.Insert(1, 1);
    assert(a.vertices.empty() && a.edge_ids.empty());
    assert(b.vertices.empty() && b.edge_ids.empty());
    auto more = edges;
    more.push_back({1, 1});
    auto expected = brute(n, more, 0);
    assert(a.run() == expected.has_value() && b.Run() == expected.has_value());
    if (expected)
    {
        assert(a.vertices == *expected && b.vertices == *expected);
        certificate(more, a.vertices, a.edge_ids);
        certificate(more, b.vertices, b.edge_ids);
    }
}

void *large(void *)
{
    constexpr int m = 200000;
    UndirectedEuler a(3);
    static Undirected_Euler<3> b;
    b.Init(3);
    vector<pair<int, int>> edges;
    // Vertex 1 is isolated; all m edges must be traversed, requiring O(m) recursion.
    for (int i = 0; i < m; i++)
    {
        int u = i % 2 + 2, v = 5 - u;
        a.add(u, v);
        b.Insert(u, v);
        edges.push_back({u, v});
    }
    assert(!a.run(1) && !b.Run(1));
    assert(a.run() && b.Run());
    certificate(edges, a.vertices, a.edge_ids);
    certificate(edges, b.vertices, b.edge_ids);
    assert(a.vertices.front() == 2 && a.vertices.back() == 2);
    return nullptr;
}

int main()
{
    for (int n = 1; n <= 3; n++)
    {
        vector<pair<int, int>> possible;
        for (int u = 1; u <= n; u++)
            for (int v = u; v <= n; v++)
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
    for (int mask = 0; mask < 81; mask++)
    {
        int code = mask;
        vector<pair<int, int>> edges;
        for (int u = 1; u <= 2; u++)
            for (int v = 1; v <= 2; v++)
            {
                int count = code % 3;
                code /= 3;
                while (count--)
                    edges.push_back({u, v});
            }
        check(2, edges);
    }
    mt19937 rng(7771);
    for (int t = 0; t < 300; t++)
    {
        int n = rng() % 6 + 1, m = rng() % 8;
        vector<pair<int, int>> edges;
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
    cout << "Undirected Euler dual exhaustive trails, lexicographic optimum, edge certificates, loops and 200000 recursive edges PASS\n";
}
