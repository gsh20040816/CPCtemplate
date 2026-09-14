#include "../src/compact/edge_components.hpp"
#include "../src/classic/edge_components.hpp"
#include <iostream>
#include <numeric>
#include <random>
#include <pthread.h>

vector<vector<bool>> reachability(int n,const vector<pair<int,int>> &edges,bool directed)
{
    vector<vector<bool>> r(n+1,vector<bool>(n+1));
    for (int u = 1; u <= n; u++)
        r[u][u] = true;
    for (auto [u,v] : edges)
    {
        r[u][v] = true;
        if (!directed)
            r[v][u] = true;
    }
    for (int k = 1; k <= n; k++)
        for (int u = 1; u <= n; u++)
            for (int v = 1; v <= n; v++)
                r[u][v] = r[u][v] || (r[u][k] && r[k][v]);
    return r;
}

void check(int n,const vector<pair<int,int>> &edges)
{
    Lowlink a(n);
    Low_Link b(n);
    BiconnectedCore c(n);
    static Biconnected_Graph<10> d;
    d.Init(n);
    for (auto [u,v] : edges)
    {
        a.add(u,v);
        b.Insert(u,v);
        c.add(u,v);
        d.Insert(u,v);
    }
    auto original = reachability(n,edges,false);
    vector<pair<int,int>> remaining;
    vector<int> bridges;
    for (int id = 0; id < (int)edges.size(); id++)
    {
        auto without = edges;
        without.erase(without.begin()+id);
        auto r = reachability(n,without,false);
        if (r != original)
            bridges.push_back(id);
        else
            remaining.push_back(edges[id]);
    }
    auto expected = reachability(n,remaining,false);
    // Orientation is independent of any existing run() state.
    auto direction = orient_edges(a);
    auto classic_direction = Orient_Edges(b);
    assert(direction == classic_direction && direction.size() == edges.size());
    for (int id = 0; id < (int)edges.size(); id++)
    {
        auto [u,v] = edges[id];
        assert(direction[id] == make_pair(u,v) || direction[id] == make_pair(v,u));
    }
    auto directed = reachability(n,direction,true);
    for (int u = 1; u <= n; u++)
        for (int v = 1; v <= n; v++)
            assert((directed[u][v] && directed[v][u]) == expected[u][v]);
    c.run();
    d.Run();
    EdgeCompression x(c);
    Edge_Compression y(d);
    for (int style = 0; style < 2; style++)
    {
        const auto &sizes = style ? y.size : x.size;
        const auto &inside = style ? y.inside : x.inside;
        const auto &forest = style ? y.edges : x.edges;
        int count = style ? y.n : x.n;
        auto label = [&](int u)
        {
            return style ? d.bel[u] : c.bel[u];
        };
        vector<int> ids;
        assert(sizes.size() == size_t(count+1) && inside.size() == sizes.size());
        assert(accumulate(sizes.begin(),sizes.end(),0) == n);
        assert(accumulate(inside.begin(),inside.end(),0)+(int)forest.size() == (int)edges.size());
        for (int u = 1; u <= n; u++)
            for (int v = 1; v <= n; v++)
                assert((label(u) == label(v)) == expected[u][v]);
        for (int k = 1; k <= count; k++)
        {
            int vertices = 0, internal = 0;
            for (int u = 1; u <= n; u++)
                vertices += label(u) == k;
            for (auto [u,v] : edges)
                internal += label(u) == k && label(v) == k;
            assert(sizes[k] == vertices && inside[k] == internal);
        }
        for (auto [u,v,id] : forest)
        {
            assert(u == label(edges[id].first) && v == label(edges[id].second));
            ids.push_back(id);
        }
        assert(ids == bridges);
    }
    a.run();
    b.Run();
    assert(orient_edges(a) == direction && Orient_Edges(b) == direction);
}

void run()
{
    check(0,{});
    for (int n = 1; n <= 4; n++)
    {
        vector<pair<int,int>> pairs;
        for (int u = 1; u <= n; u++)
            for (int v = u; v <= n; v++)
                pairs.push_back({u,v});
        for (int mask = 0; mask < (1 << pairs.size()); mask++)
        {
            vector<pair<int,int>> edges;
            for (int i = 0; i < (int)pairs.size(); i++)
                if (mask >> i & 1)
                    edges.push_back(pairs[i]);
            check(n,edges);
        }
    }
    mt19937 rng(118);
    for (int trial = 0; trial < 1500; trial++)
    {
        int n = 1+rng()%10;
        vector<pair<int,int>> edges;
        for (int m = rng()%25; m--;)
            edges.emplace_back(1+rng()%n,1+rng()%n);
        check(n,edges);
    }
    const int n = 200000;
    Lowlink a(n);
    Low_Link b(n);
    for (int u = 1; u < n; u++)
    {
        a.add(u,u+1);
        b.Insert(u,u+1);
    }
    a.add(n,1);
    b.Insert(n,1);
    auto x = orient_edges(a), y = Orient_Edges(b);
    assert(x == y && (int)x.size() == n);
    for (int i = 0; i < n; i++)
        assert(x[i] == make_pair(i+1,(i+1)%n+1));
    cout << "Edge compression/orientation dual removal and reachability oracles, multigraph IDs and recursive cycle PASS\n";
}

void *worker(void *)
{
    run();
    return nullptr;
}

int main()
{
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr,256ULL<<20) == 0);
    pthread_t thread;
    assert(pthread_create(&thread,&attr,worker,nullptr) == 0);
    assert(pthread_attr_destroy(&attr) == 0);
    assert(pthread_join(thread,nullptr) == 0);
}
