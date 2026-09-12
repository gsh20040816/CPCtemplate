#include <cstdio>
#include "../../src/compact/functional_graph.hpp"

int main()
{
    int n;
    scanf("%d", &n);
    vector<int> to(n);
    for (auto &v : to)
    {
        scanf("%d", &v);
        v--;
    }
    FunctionalGraph graph(to);
    for (int u = 0; u < n; u++)
        printf("%d\n", graph.depth[u] + int(graph.cycles[graph.component[u]].size()));
}
