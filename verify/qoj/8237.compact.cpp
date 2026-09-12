#include <cstdio>
#include "../../src/compact/functional_graph.hpp"
#include "../../src/compact/number_theory.hpp"

int main()
{
    int tests;
    scanf("%d", &tests);
    using Z = ModInt<1000000007>;
    Binomial<1000000007> factorial;
    FunctionalGraph graph;
    while (tests--)
    {
        int n;
        scanf("%d", &n);
        vector<int> a(n), b(n), w(n);
        for (auto &x : a) scanf("%d", &x);
        for (auto &x : b)
        {
            scanf("%d", &x);
            x--;
        }
        for (auto &x : w) scanf("%d", &x);
        vector<char> certain(n);
        for (int u = 0; u < n; u++)
        {
            int v = b[u];
            if (a[u] < a[v])
            {
                certain[u] = true;
                b[u] = u;
            }
            else if (a[u] >= a[v] + 1LL * w[v])
                b[u] = u;
        }
        graph.build(move(b));
        factorial.init(n);
        for (int u = 0; u < n; u++)
        {
            Z probability = 0;
            if (certain[graph.entry[u]])
                probability = factorial.ifac[graph.depth[u] + 1];
            Z answer = Z(a[u]) + Z(w[u]) * probability;
            printf("%d%c", answer.v, u + 1 == n ? '\n' : ' ');
        }
    }
}
