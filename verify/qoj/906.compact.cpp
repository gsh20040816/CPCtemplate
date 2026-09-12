#include <cstdio>
#include "../../src/compact/tarjan.hpp"

int main()
{
    int n, m;
    scanf("%d%d", &n, &m);
    TarjanSCC g(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        scanf("%d%d", &u, &v);
        g.add(u + 1, v + 1);
    }
    g.run();
    vector<vector<int>> s(g.cnt + 1);
    for (int u = 1; u <= n; u++)
        s[g.bel[u]].push_back(u - 1);
    printf("%d\n", g.cnt);
    for (int i = g.cnt; i > 0; i--)
    {
        printf("%d", int(s[i].size()));
        for (int u : s[i])
            printf(" %d", u);
        printf("\n");
    }
    return 0;
}
