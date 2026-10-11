#include "../src/compact/dynamic_diameter.hpp"

int main()
{
    const int n = 100000;
    const long long initial = 19999999999999LL;
    for (int shape = 0; shape < 3; shape++)
    {
        DynamicDiameter tree(n);
        for (int u = 2; u <= n; u++) tree.add(shape == 0 ? u - 1 : 1, u, initial);
        tree.build();
        long long total = (n - 1) * initial;
        multiset<long long> weights;
        for (int i = 1; i < n; i++) weights.insert(initial);
        for (int q = 0; q < 100000; q++)
        {
            int id = q % (n - 1);
            long long w = q % 2 ? initial : 0;
            total += w - tree.edges[id].w;
            weights.erase(weights.find(tree.edges[id].w));
            weights.insert(w);
            tree.update(id, w);
            long long expected = total;
            if (shape != 0)
            {
                auto it = weights.rbegin();
                expected = *it;
                expected += *++it;
            }
            if (tree.diameter() != expected) abort();
            if (shape == 2 && q % 10000 == 0) tree.build(n);
        }
        cout << "PASS shape=" << shape << " n=" << n << " q=100000\n";
    }
}
