#include <cstdio>
#include "../../src/compact/functional_graph.hpp"

int main()
{
    int n, q;
    scanf("%d%d", &n, &q);
    vector<int> to(n);
    for (auto &v : to)
    {
        scanf("%d", &v);
        v--;
    }
    FunctionalGraph graph(to);
    while (q--)
    {
        int u, v;
        scanf("%d%d", &u, &v);
        printf("%d\n", graph.steps(u - 1, v - 1));
    }
}
