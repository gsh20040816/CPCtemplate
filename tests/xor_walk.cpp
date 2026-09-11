#include "../src/compact/xor_walk.hpp"
#include "../src/classic/xor_walk.hpp"
#include <iostream>
#include <queue>
#include <random>
#include <pthread.h>
using U = unsigned long long;
using Edge = tuple<int,int,U>;

void check(int n, const vector<Edge> &edges)
{
    XorWalk a(n);
    static Xor_Walk<10> b;
    b.Init(n);
    vector<vector<pair<int,U>>> g(n+1);
    for (auto [u,v,w] : edges)
    {
        a.add(u,v,w);
        b.Insert(u,v,w);
        g[u].push_back({v,w});
        g[v].push_back({u,w});
    }
    vector<vector<optional<U>>> want(n+1,vector<optional<U>>(n+1));
    // Product graph: (vertex, accumulated XOR), independently explores all walks.
    for (int s = 1; s <= n; s++)
    {
        vector<array<bool,8>> seen(n+1);
        queue<pair<int,int>> q;
        q.push({s,0});
        seen[s][0] = true;
        while (!q.empty())
        {
            auto [u,x] = q.front();
            q.pop();
            for (auto [v,w] : g[u])
                if (!seen[v][x^w])
                {
                    seen[v][x^w] = true;
                    q.push({v,x^w});
                }
        }
        for (int v = 1; v <= n; v++)
            for (int x = 0; x < 8; x++)
                if (seen[v][x])
                    want[s][v] = x;
    }
    for (int root = 1; root <= n; root++)
    {
        a.build(root);
        b.Build(root);
        for (int u = 1; u <= n; u++)
            for (int v = 1; v <= n; v++)
            {
                auto expected = want[root][u] && want[root][v] ? want[u][v] : nullopt;
                assert(a.query(u,v) == expected);
                assert(b.Query(u,v) == expected);
            }
    }
}

void run()
{
    for (int n = 1; n <= 3; n++)
    {
        vector<pair<int,int>> pairs;
        for (int u = 1; u <= n; u++)
            for (int v = u; v <= n; v++)
                pairs.push_back({u,v});
        int total = 1 << (2*pairs.size());
        for (int code = 0; code < total; code++)
        {
            vector<Edge> edges;
            int x = code;
            for (auto [u,v] : pairs)
            {
                int state = x%4;
                x /= 4;
                if (state)
                    edges.emplace_back(u,v,vector<U>{0,0,1,3}[state]);
            }
            check(n,edges);
        }
    }
    mt19937_64 rng(4151);
    for (int trial = 0; trial < 600; trial++)
    {
        int n = 1+rng()%8;
        vector<Edge> edges;
        for (int m = rng()%25; m--;)
            edges.emplace_back(1+rng()%n,1+rng()%n,rng()%8);
        check(n,edges);
    }
    XorWalk a(3);
    static Xor_Walk<200000> b;
    b.Init(3);
    U x = (1ULL<<63)+17, y = ~0ULL;
    a.add(1,2,x);
    a.add(1,2,y);
    b.Insert(1,2,x);
    b.Insert(1,2,y);
    a.build();
    b.Build();
    assert(a.query(1,2) == y && b.Query(1,2) == y);
    assert(a.query(1,1) == (x^y) && b.Query(1,1) == (x^y));
    assert(!a.query(1,3) && !b.Query(1,3));
    for (int i = 0; i < 64; i++)
    {
        a.add(1,1,1ULL<<i);
        b.Insert(1,1,1ULL<<i);
    }
    assert(!a.built && !b.built);
    a.build(2);
    b.Build(2);
    assert(a.query(1,2) == ~0ULL && b.Query(1,2) == ~0ULL);
    a.build(3);
    b.Build(3);
    assert(a.query(3,3) == 0 && b.Query(3,3) == 0);
    assert(!a.query(1,2) && !b.Query(1,2));
    const int n = 200000;
    a.init(n);
    b.Init(n);
    for (int i = 1; i < n; i++)
    {
        a.add(i,i+1,1);
        b.Insert(i,i+1,1);
    }
    a.build();
    b.Build();
    assert(a.query(1,n) == 1 && b.Query(1,n) == 1);
    a.build(n);
    b.Build(n);
    assert(a.query(1,n-1) == 0 && b.Query(1,n-1) == 0);
    a.init(1);
    b.Init(1);
    a.build();
    b.Build();
    assert(a.query(1,1) == 0 && b.Query(1,1) == 0);
    cout << "XOR walk dual product-graph oracle, loops, parallel edges, components and recursive chain PASS\n";
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
