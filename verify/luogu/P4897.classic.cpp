#include "../../src/classic/gomory_hu.hpp"
#include "../../src/classic/cut_tree_queries.hpp"
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
