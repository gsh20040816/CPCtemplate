#include <cstdio>
#include "../../src/classic/functional_graph.hpp"

int main()
{
    int n;
    scanf("%d", &n);
    vector<int> to(n);
    for ( auto &v : to )
    {
        scanf("%d", &v);
        v--;
    }
    Functional_Graph graph(to);
    for ( int u = 0; u < n; u++ )
        printf("%d\n", graph.depth[u] + int(graph.cycles[graph.component[u]].size()));
}
