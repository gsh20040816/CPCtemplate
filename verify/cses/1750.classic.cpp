#include <cstdio>
#include "../../src/classic/functional_graph.hpp"

int main()
{
    int n, q;
    scanf("%d%d", &n, &q);
    vector<int> to(n);
    for ( auto &v : to )
    {
        scanf("%d", &v);
        v--;
    }
    Functional_Graph graph(to);
    while ( q-- )
    {
        int u;
        unsigned long long k;
        scanf("%d%llu", &u, &k);
        printf("%d\n", graph.Advance(u - 1, k) + 1);
    }
}
