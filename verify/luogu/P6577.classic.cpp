#include "../../src/classic/weighted_matching.hpp"
#include <cstdio>

Weighted_Matching<500, 500> graph;

int main()
{
    int n, m;
    scanf("%d%d", &n, &m);
    graph.Init(n, n);
    while ( m-- )
    {
        int x, y;
        long long w;
        scanf("%d%d%lld", &x, &y, &w);
        graph.Insert(x, y, w);
    }
    auto answer = graph.Solve();
    assert(answer);
    printf("%lld\n", (long long)*answer);
    for ( int j = 1; j <= n; j++ )
        printf("%d%c", graph.r[j], j == n ? '\n' : ' ');
}
