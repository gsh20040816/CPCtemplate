#include <algorithm>
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

// N vertices, M original directed edges, IDs 0,2,4,... .
template <int N, int M> struct Network_Flow
{
    using ll = long long;

    struct Edge
    {
        int to, next;
        ll cap, initial;
    } edge[2 * M];

    int n, tot, head[N + 1], deep[N + 1], cur[N + 1], que[N + 1];

    void Init(int size)
    {
        assert(size <= N);
        n = size;
        tot = 0;
        fill(head, head + n + 1, -1);
    }

    int Add_Edge(int u, int v, ll cap)
    {
        assert(cap >= 0 && tot + 2 <= 2 * M);
        int id = tot;
        edge[tot] = {v, head[u], cap, cap};
        head[u] = tot++;
        edge[tot] = {u, head[v], 0, 0};
        head[v] = tot++;
        return id;
    }

    bool Bfs(int s, int t)
    {
        fill(deep, deep + n + 1, -1);
        int L = 0, R = 0;
        que[R++] = s;
        deep[s] = 0;
        while ( L < R )
        {
            int now = que[L++];
            for ( int i = head[now]; i != -1; i = edge[i].next )
            {
                int to = edge[i].to;
                if ( edge[i].cap && deep[to] == -1 )
                {
                    deep[to] = deep[now] + 1;
                    que[R++] = to;
                }
            }
        }
        return deep[t] != -1;
    }

    ll Dfs(int now, int t, ll flow)
    {
        if ( now == t )
            return flow;
        for ( int &i = cur[now]; i != -1; i = edge[i].next )
        {
            int to = edge[i].to;
            if ( !edge[i].cap || deep[to] != deep[now] + 1 )
                continue;
            ll delta = Dfs(to, t, min(flow, edge[i].cap));
            if ( delta )
            {
                edge[i].cap -= delta;
                edge[i ^ 1].cap += delta;
                return delta;
            }
        }
        return 0;
    }

    ll Max_Flow(int s, int t, ll limit = LLONG_MAX)
    {
        assert(s != t && limit >= 0);
        ll answer = 0;
        while ( answer < limit && Bfs(s, t) )
        {
            copy(head, head + n + 1, cur);
            while ( answer < limit )
            {
                ll delta = Dfs(s, t, limit - answer);
                if ( !delta )
                    break;
                answer += delta;
            }
        }
        return answer;
    }

    ll Used(int id) const
    {
        return edge[id].initial - edge[id].cap;
    }

    vector<int> Cut(int s)
    {
        Bfs(s, s);
        vector<int> answer;
        for ( int i = 1; i <= n; i++ )
            if ( deep[i] != -1 )
                answer.push_back(i);
        return answer;
    }
};

template <int N, int M> struct Bounded_Circulation
{
    int n, tot;
    Network_Flow<N + 2, M + N> graph;
    long long balance[N + 1], lower[M];
    int id[M];
    bool solved, feasible;

    void Init(int size)
    {
        assert(size <= N);
        n = size;
        tot = 0;
        solved = feasible = false;
        graph.Init(n + 2);
        fill(balance, balance + n + 1, 0);
    }

    int Insert(int u, int v, long long L, long long R)
    {
        assert(!solved && 0 <= L && L <= R && tot < M);
        id[tot] = graph.Add_Edge(u, v, R - L);
        lower[tot] = L;
        balance[u] -= L;
        balance[v] += L;
        return tot++;
    }

    bool Solve()
    {
        assert(!solved);
        solved = true;
        long long need = 0;
        for ( int u = 1; u <= n; u++ )
        {
            if ( balance[u] > 0 )
            {
                graph.Add_Edge(n + 1, u, balance[u]);
                need += balance[u];
            }
            else if ( balance[u] < 0 )
                graph.Add_Edge(u, n + 2, -balance[u]);
        }
        return feasible = (graph.Max_Flow(n + 1, n + 2) == need);
    }

    long long Used(int index) const
    {
        assert(feasible);
        return lower[index] + graph.Used(id[index]);
    }
};

#include <tuple>

// BEGIN Gomory_Hu
template <int N, int M>
vector<tuple<int, int, long long>> Gomory_Hu(
    int n, const vector<tuple<int, int, long long>> &edges, Network_Flow<N, M> &flow)
{
    assert(n >= 1);
    vector<int> parent(n);
    vector<long long> value(n);
    for ( int s = 1; s < n; s++ )
    {
        int t = parent[s];
        flow.Init(n);
        for ( auto [u, v, w] : edges )
            if ( u != v )
            {
                flow.Add_Edge(u + 1, v + 1, w);
                flow.Add_Edge(v + 1, u + 1, w);
            }
        long long cut = flow.Max_Flow(s + 1, t + 1);
        vector<bool> side(n);
        for ( int u : flow.Cut(s + 1) )
            side[u - 1] = true;
        for ( int v = 1; v < n; v++ )
            if ( v != s && parent[v] == t && side[v] )
                parent[v] = s;
        if ( side[parent[t]] )
        {
            parent[s] = parent[t];
            parent[t] = s;
            value[s] = value[t];
            value[t] = cut;
        }
        else
            value[s] = cut;
    }
    vector<tuple<int, int, long long>> tree;
    for ( int v = 1; v < n; v++ )
        tree.push_back({v, parent[v], value[v]});
    return tree;
}

// END Gomory_Hu

#include <algorithm>
#include <cassert>
#include <climits>
#include <tuple>
#include <vector>
using namespace std;

// BEGIN Cut_Tree_Values
inline vector<vector<long long>>
Cut_Tree_Values(int n, const vector<tuple<int, int, long long>> &tree)
{
    assert(n >= 1 && tree.size() == (size_t)n - 1);
    vector<vector<pair<int, long long>>> g(n);
    for ( auto [u, v, w] : tree )
    {
        assert(0 <= u && u < n && 0 <= v && v < n && w >= 0);
        g[u].push_back({v, w});
        g[v].push_back({u, w});
    }
    vector<vector<long long>> answer(n, vector<long long>(n, LLONG_MAX));
    for ( int s = 0; s < n; s++ )
    {
        auto dfs = [&](auto &&self, int u, int parent, long long value) -> void
        {
            answer[s][u] = value;
            for ( auto [v, w] : g[u] )
                if ( v != parent )
                    self(self, v, u, min(value, w));
        };
        dfs(dfs, s, -1, LLONG_MAX);
    }
    return answer;
}

// END Cut_Tree_Values

#include <cstdio>

static Network_Flow<501, 3000> flow;

int main()
{
    int n, m;
    scanf("%d%d", &n, &m);
    vector<tuple<int, int, long long>> edges;
    for ( int i = 0; i < m; i++ )
    {
        int u, v;
        long long w;
        scanf("%d%d%lld", &u, &v, &w);
        edges.push_back({u, v, w});
    }
    auto tree = Gomory_Hu(n + 1, edges, flow);
    auto answer = Cut_Tree_Values(n + 1, tree);
    int q;
    scanf("%d", &q);
    while ( q-- )
    {
        int u, v;
        scanf("%d%d", &u, &v);
        printf("%lld\n", answer[u][v]);
    }
    return 0;
}
