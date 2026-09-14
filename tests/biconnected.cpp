#include "../src/compact/block_cut_forest.hpp"
#include "../src/compact/bridge_component_forest.hpp"
#include "../src/classic/biconnected.hpp"
#include <iostream>
#include <random>
#include <set>
#include <pthread.h>

using Edges = std::vector<std::pair<int, int>>;
std::vector<int> components(int n, const Edges &e, unsigned vertices, int skip = -1)
{
    std::vector<int> label(n + 1);
    int count = 0;
    for (int u = 1; u <= n; u++)
    {
        if (!(vertices >> (u - 1) & 1) || label[u])
            continue;
        label[u] = ++count;
        std::vector<int> q{u};
        for (int i = 0; i < (int)q.size(); i++)
        {
            for (int id = 0; id < (int)e.size(); id++)
            {
                if (id == skip)
                    continue;
                auto [a, b] = e[id];
                if (b == q[i])
                    std::swap(a, b);
                if (a == q[i] && (vertices >> (b - 1) & 1) && !label[b])
                {
                    label[b] = count;
                    q.push_back(b);
                }
            }
        }
    }
    return label;
}

void check(int n, const Edges &e)
{
    unsigned all = (1U << n) - 1;
    auto full = components(n, e, all);
    int nc = *std::max_element(full.begin(), full.end());
    std::set<unsigned> expected;
    std::vector<unsigned> candidates;
    for (unsigned mask = 1; mask <= all; mask++)
    {
        auto c = components(n, e, mask);
        bool good = *std::max_element(c.begin(), c.end()) == 1;
        for (int u = 1; u <= n && good; u++)
        {
            if (!(mask >> (u - 1) & 1))
                continue;
            c = components(n, e, mask ^ (1U << (u - 1)));
            good &= *std::max_element(c.begin(), c.end()) <= 1;
        }
        if (good)
            candidates.push_back(mask);
    }
    for (unsigned mask : candidates)
    {
        bool maximal = true;
        for (unsigned other : candidates)
            if (mask != other && (mask & other) == mask)
                maximal = false;
        if (maximal)
            expected.insert(mask);
    }
    std::vector<int> bridges(e.size());
    Edges remaining;
    for (int id = 0; id < (int)e.size(); id++)
    {
        auto c = components(n, e, all, id);
        bridges[id] = *std::max_element(c.begin(), c.end()) > nc;
        if (!bridges[id])
            remaining.push_back(e[id]);
    }
    auto edge_components = components(n, remaining, all);
    BiconnectedCore a(n);
    static Biconnected_Graph<8> b;
    b.Init(n);
    for (auto [u, v] : e)
    {
        a.add(u, v);
        b.Insert(u, v);
    }
    for (int repeat = 0; repeat < 2; repeat++)
    {
        a.run();
        b.Run();
        assert(a.st.empty() && b.st.empty());
        assert(a.bridge == bridges && b.bridge == bridges);
        for (auto blocks : {a.blocks, b.blocks})
        {
            std::set<unsigned> actual;
            for (auto block : blocks)
            {
                unsigned mask = 0;
                for (int u : block)
                {
                    assert(!(mask >> (u - 1) & 1));
                    mask |= 1U << (u - 1);
                }
                assert(actual.insert(mask).second);
            }
            assert(actual == expected);
        }
        for (int u = 1; u <= n; u++)
        {
            auto c = components(n, e, all ^ (1U << (u - 1)));
            bool cut = *std::max_element(c.begin(), c.end()) > nc;
            assert(a.cut[u] == cut && b.cut[u] == cut);
            for (int v = 1; v <= n; v++)
            {
                bool same = edge_components[u] == edge_components[v];
                assert((a.bel[u] == a.bel[v]) == same);
                assert((b.bel[u] == b.bel[v]) == same);
            }
        }
        for (auto tree : {block_cut_forest(a), b.Block_Forest()})
        {
            int nodes = tree.size() - 1;
            Edges te;
            for (int u = 1; u <= nodes; u++)
                for (int v : tree[u])
                    if (u < v)
                        te.push_back({u, v});
            assert((int)te.size() == nodes - nc);
            auto c = components(nodes, te, (1U << nodes) - 1);
            for (int u = 1; u <= n; u++)
                for (int v = 1; v <= n; v++)
                    assert((c[u] == c[v]) == (full[u] == full[v]));
        }
        for (int style = 0; style < 2; style++)
        {
            auto tree = style ? b.Bridge_Forest() : bridge_component_forest(a);
            int count = 0;
            for (int u = 1; u < (int)tree.size(); u++)
            {
                for (auto [v, id] : tree[u])
                {
                    assert(bridges[id]);
                    auto [x, y] = e[id];
                    x = style ? b.bel[x] : a.bel[x];
                    y = style ? b.bel[y] : a.bel[y];
                    assert((x == u && y == v) || (x == v && y == u));
                    count++;
                }
            }
            assert(count == 2 * (int)std::count(bridges.begin(), bridges.end(), 1));
        }
    }
}

void test_all()
{
    check(0, {});
    for (unsigned mask = 0; mask < 1024; mask++)
    {
        Edges e;
        int bit = 0;
        for (int u = 1; u <= 5; u++)
            for (int v = u + 1; v <= 5; v++)
                if (mask >> bit++ & 1)
                    e.push_back({u, v});
        check(5, e);
    }
    std::mt19937 rng(774631);
    for (int trial = 0; trial < 1500; trial++)
    {
        int n = 1 + rng() % 8;
        Edges e;
        int m = rng() % 20;
        for (int i = 0; i < m; i++)
            e.push_back({1 + rng() % n, 1 + rng() % n});
        check(n, e);
    }
    const int n = 200000;
    BiconnectedCore a(n);
    static Biconnected_Graph<n> b;
    b.Init(n);
    for (int u = 1; u < n; u++)
    {
        a.add(u, u + 1);
        b.Insert(u, u + 1);
    }
    a.run();
    b.Run();
    assert(a.cnt == n && b.cnt == n);
    assert(a.blocks.size() == n - 1 && b.blocks.size() == n - 1);
    for (int id = 0; id < n - 1; id++)
        assert(a.bridge[id] && b.bridge[id]);
    a.add(n, 1);
    b.Insert(n, 1);
    a.run();
    b.Run();
    assert(a.cnt == 1 && b.cnt == 1);
    assert(a.blocks.size() == 1 && b.blocks.size() == 1);
    assert(a.blocks[0].size() == n && b.blocks[0].size() == n);
    std::cout << "Biconnected subset/removal oracles and block/bridge forests PASS\n";
}

void *test_entry(void *)
{
    test_all();
    return nullptr;
}

int main()
{
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, 256ULL << 20) == 0);
    pthread_t thread;
    assert(pthread_create(&thread, &attr, test_entry, nullptr) == 0);
    assert(pthread_attr_destroy(&attr) == 0);
    assert(pthread_join(thread, nullptr) == 0);
}
