#include "../../src/compact/matrix_tree_mod.hpp"

int main()
{
    using M = MatrixTreeMod;
    int n, m, type;
    scanf("%d%d%d", &n, &m, &type);
    vector<M::Edge> edges;
    for (int i = 0; i < m; i++)
    {
        int u, v;
        long long w;
        scanf("%d%d%lld", &u, &v, &w);
        edges.push_back({u - 1, v - 1, w});
    }
    auto kind = type ? M::Kind::away_from_root : M::Kind::undirected;
    printf("%lld\n", M::count(n, edges, 0, kind, 1000000007));
}
