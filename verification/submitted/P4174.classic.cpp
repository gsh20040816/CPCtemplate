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


// BEGIN Maximum_Closure
template <int N, int M>
pair<long long, vector<int>> Maximum_Closure(const vector<long long> &weight,
                                             const vector<pair<int, int>> &dependencies,
                                             Network_Flow<N, M> &graph)
{
    using I = __int128_t;
    int n = weight.size(), s = n + 1, t = n + 2;
    I positive = 0;
    for ( long long w : weight )
        if ( w > 0 )
            positive += w;
    assert(positive < LLONG_MAX);
    long long inf = (long long)positive + 1;
    graph.Init(n + 2);
    for ( int u = 1; u <= n; u++ )
    {
        long long w = weight[u - 1];
        if ( w > 0 )
            graph.Add_Edge(s, u, w);
        else if ( w < 0 )
            graph.Add_Edge(u, t, (long long)min(-I(w), I(inf)));
    }
    for ( auto [u, v] : dependencies )
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        graph.Add_Edge(u, v, inf);
    }
    long long answer = (long long)positive - graph.Max_Flow(s, t);
    vector<int> selected;
    for ( int u : graph.Cut(s) )
        if ( u <= n )
            selected.push_back(u);
    return {answer, selected};
}

// END Maximum_Closure

#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    std::vector<long long> weight(n + m);
    for ( int i = 0; i < n; i++ )
    {
        long long cost;
        std::cin >> cost;
        weight[i] = -cost;
    }
    std::vector<std::pair<int, int>> dependencies;
    for ( int i = 1; i <= m; i++ )
    {
        int u, v;
        long long profit;
        std::cin >> u >> v >> profit;
        weight[n + i - 1] = profit;
        dependencies.push_back({n + i, u});
        dependencies.push_back({n + i, v});
    }
    static Network_Flow<55002, 155000> graph;
    auto answer = Maximum_Closure(weight, dependencies, graph);
    std::cout << answer.first << '\n';
}
