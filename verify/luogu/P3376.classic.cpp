#include "../../src/classic/flow.hpp"
#include <cstdio>
Network_Flow<205, 5005> Graph;

int main()
{
    int n, m, s, t;
    scanf("%d%d%d%d", &n, &m, &s, &t);
    Graph.Init(n);
    for ( int i = 1; i <= m; i++ )
    {
        int u, v;
        long long cap;
        scanf("%d%d%lld", &u, &v, &cap);
        Graph.Add_Edge(u, v, cap);
    }
    printf("%lld\n", Graph.Max_Flow(s, t));
    return 0;
}
