#include <algorithm>
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

// N vertices, M original directed edges, IDs 0,2,4,... .
template<int N, int M> struct Network_Flow
{
    using ll = long long;
    struct Edge { int to, next; ll cap, initial; } edge[2 * M];
    int n, tot, head[N + 1], deep[N + 1], cur[N + 1], que[N + 1];
    void Init ( int size )
    {
        assert(size <= N); n = size; tot = 0;
        fill(head, head + n + 1, -1);
    }
    int Add_Edge ( int u, int v, ll cap )
    {
        assert(cap >= 0 && tot + 2 <= 2 * M);
        int id = tot;
        edge[tot] = {v, head[u], cap, cap}; head[u] = tot ++;
        edge[tot] = {u, head[v], 0, 0}; head[v] = tot ++;
        return id;
    }
    bool Bfs ( int s, int t )
    {
        fill(deep, deep + n + 1, -1);
        int L = 0, R = 0; que[R ++] = s; deep[s] = 0;
        while ( L < R )
        {
            int now = que[L ++];
            for ( int i = head[now]; i != -1; i = edge[i].next )
            {
                int to = edge[i].to;
                if ( edge[i].cap && deep[to] == -1 )
                { deep[to] = deep[now] + 1; que[R ++] = to; }
            }
        }
        return deep[t] != -1;
    }
    ll Dfs ( int now, int t, ll flow )
    {
        if ( now == t ) return flow;
        for ( int &i = cur[now]; i != -1; i = edge[i].next )
        {
            int to = edge[i].to;
            if ( !edge[i].cap || deep[to] != deep[now] + 1 ) continue;
            ll delta = Dfs(to, t, min(flow, edge[i].cap));
            if ( delta )
            { edge[i].cap -= delta; edge[i ^ 1].cap += delta; return delta; }
        }
        return 0;
    }
    ll Max_Flow ( int s, int t, ll limit = LLONG_MAX )
    {
        assert(s != t && limit >= 0); ll answer = 0;
        while ( answer < limit && Bfs(s, t) )
        {
            copy(head, head + n + 1, cur);
            while ( answer < limit )
            {
                ll delta = Dfs(s, t, limit - answer);
                if ( !delta ) break;
                answer += delta;
            }
        }
        return answer;
    }
    ll Used ( int id ) const { return edge[id].initial - edge[id].cap; }
    vector<int> Cut ( int s )
    {
        Bfs(s, s); vector<int> answer;
        for ( int i = 1; i <= n; i ++ ) if ( deep[i] != -1 ) answer.push_back(i);
        return answer;
    }
};

#include <cstdio>
Network_Flow<205,5005> Graph;
int main ()
{
    int n, m, s, t;
    scanf("%d%d%d%d", &n, &m, &s, &t);
    Graph.Init(n);
    for ( int i = 1; i <= m; i ++ )
    {
        int u, v; long long cap;
        scanf("%d%d%lld", &u, &v, &cap);
        Graph.Add_Edge(u, v, cap);
    }
    printf("%lld\n", Graph.Max_Flow(s, t));
    return 0;
}
