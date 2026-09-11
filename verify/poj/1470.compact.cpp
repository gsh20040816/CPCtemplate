#include "../../src/compact/offline_lca.hpp"
#include <cstdio>

int main()
{
    int n;
    while (scanf("%d", &n) == 1)
    {
        OfflineLCA graph(n);
        vector<int> has_parent(n + 1), count(n + 1);
        for (int i = 0; i < n; i++)
        {
            int u, k;
            scanf(" %d : ( %d )", &u, &k);
            while (k--)
            {
                int v;
                scanf("%d", &v);
                graph.add(u, v);
                has_parent[v] = 1;
            }
        }
        int q;
        scanf("%d", &q);
        while (q--)
        {
            int u, v;
            scanf(" ( %d %d )", &u, &v);
            graph.add_query(u, v);
        }
        int root = 1;
        while (has_parent[root])
            root++;
        graph.run(root);
        for (int u : graph.answer)
            count[u]++;
        for (int u = 1; u <= n; u++)
            if (count[u])
                printf("%d:%d\n", u, count[u]);
    }
    return 0;
}
