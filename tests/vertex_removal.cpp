#include "../src/compact/vertex_removal.hpp"
#include "../src/classic/vertex_removal.hpp"
#include "../src/compact/graph.hpp"
#include "../src/classic/graph.hpp"
#include <iostream>
#include <random>
#include <pthread.h>

int count_components(int n, const vector<pair<int,int>> &edges, int removed)
{
    vector<vector<int>> g(n+1);
    for (auto [u,v] : edges)
        if (u != removed && v != removed)
        {
            g[u].push_back(v);
            g[v].push_back(u);
        }
    vector<bool> visited(n+1);
    int answer = 0;
    for (int u = 1; u <= n; u++)
        if (u != removed && !visited[u])
        {
            answer++;
            vector<int> q{u};
            visited[u] = true;
            for (int head = 0; head < (int)q.size(); head++)
                for (int v : g[q[head]])
                    if (!visited[v])
                    {
                        visited[v] = true;
                        q.push_back(v);
                    }
        }
    return answer;
}

void check(int n, const vector<pair<int,int>> &edges)
{
    Lowlink direct(n);
    Low_Link traditional(n);
    BiconnectedCore a(n);
    static Biconnected_Graph<12> b;
    b.Init(n);
    for (auto [u,v] : edges)
    {
        direct.add(u,v);
        traditional.Insert(u,v);
        a.add(u,v);
        b.Insert(u,v);
    }
    int before = count_components(n,edges,0);
    vector<int> after(n+1);
    for (int u = 1; u <= n; u++)
        after[u] = count_components(n,edges,u);
    auto want = make_pair(before,after);
    for (int repeat = 0; repeat < 2; repeat++)
    {
        direct.run();
        traditional.Run();
        assert(direct.components == before && traditional.components == before);
        a.run();
        b.Run();
        assert(removal_components(a) == want);
        assert(Removal_Components(b) == want);
        for (int u = 1; u <= n; u++)
        {
            assert(direct.components + direct.delta[u] == after[u]);
            assert(traditional.components + traditional.delta[u] == after[u]);
            assert(bool(a.cut[u]) == (after[u] > before));
            assert(bool(b.cut[u]) == (after[u] > before));
        }
    }
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
    mt19937 rng(2117);
    for (int trial = 0; trial < 2000; trial++)
    {
        int n = 1+rng()%12;
        vector<pair<int,int>> edges;
        for (int m = rng()%50; m--;)
            edges.emplace_back(1+rng()%n,1+rng()%n);
        check(n,edges);
    }
    const int n = 200000;
    Lowlink direct(n);
    Low_Link traditional(n);
    BiconnectedCore a(n);
    static Biconnected_Graph<n> b;
    b.Init(n);
    for (int u = 1; u < n; u++)
    {
        direct.add(u,u+1);
        traditional.Insert(u,u+1);
        a.add(u,u+1);
        b.Insert(u,u+1);
    }
    a.run();
    b.Run();
    direct.run();
    traditional.Run();
    assert(direct.components == 1 && traditional.components == 1);
    auto x = removal_components(a), y = Removal_Components(b);
    assert(x == y && x.first == 1);
    for (int u = 1; u <= n; u++)
    {
        int expected = u == 1 || u == n ? 1 : 2;
        assert(x.second[u] == expected);
        assert(direct.components + direct.delta[u] == expected);
        assert(traditional.components + traditional.delta[u] == expected);
    }
    b.Init(1);
    b.Insert(1,1);
    b.Run();
    auto one = Removal_Components(b);
    assert(one.first == 1 && one.second == vector<int>({0,0}));
    cout << "Vertex removal dual explicit deletion oracle, isolated vertices, multigraphs and recursive chain PASS\n";
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
