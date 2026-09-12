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
        int u, v;
        scanf("%d%d", &u, &v);
        printf("%d\n", graph.Steps(u - 1, v - 1));
    }
}
