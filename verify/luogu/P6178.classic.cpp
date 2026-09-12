#include "../../src/classic/matrix_tree.hpp"

int main()
{
    using M = Matrix_Tree<1000000007>;
    int n, m, type;
    scanf("%d%d%d", &n, &m, &type);
    vector<M::Edge> edges;
    for ( int i = 0; i < m; i++ )
    {
        int u, v;
        long long w;
        scanf("%d%d%lld", &u, &v, &w);
        edges.push_back({u - 1, v - 1, w});
    }
    auto kind = type ? M::Kind::away_from_root : M::Kind::undirected;
    printf("%d\n", M::Count(n, edges, 0, kind).v);
}
