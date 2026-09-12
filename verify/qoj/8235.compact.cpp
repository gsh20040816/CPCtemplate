#include <cstdio>
#include "../../src/compact/euler_lca.hpp"
#include "../../src/compact/tree_diameter.hpp"

int main()
{
    int n, q;
    scanf("%d%d", &n, &q);
    vector<int> position(n + 1, -1);
    for (int u = 1; u <= n; u++)
    {
        int w;
        scanf("%d", &w);
        if (w <= n) position[w] = u;
    }
    EulerLCA lca(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        long long w;
        scanf("%d%d%lld", &u, &v, &w);
        lca.add(u, v, w);
    }
    lca.build();
    auto distance = [&](int u, int v)
    {
        return lca.weighted_distance(u, v);
    };
    int mex = 0;
    while (position[mex] != -1) mex++;
    vector<TreeDiameter> prefix(mex + 1);
    for (int i = 0; i < mex; i++)
    {
        prefix[i + 1] = prefix[i];
        prefix[i + 1].insert(position[i], distance);
    }
    while (q--)
    {
        int x;
        long long k;
        scanf("%d%lld", &x, &k);
        int l = 0, r = mex;
        while (l < r)
        {
            int m = (l + r + 1) / 2;
            if (prefix[m].farthest(x, distance)->second <= k)
                l = m;
            else
                r = m - 1;
        }
        printf("%d\n", l);
    }
    return 0;
}
