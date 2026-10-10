#include "../src/compact/cactus.hpp"
#include <random>

int main()
{
    const int n = 100000;
    std::mt19937 rng(5236);
    for (int shape = 0; shape < 3; shape++)
    {
        Cactus a(n);
        for (int i = 1; i < n; i++) a.add(shape == 2 ? 1 : i, i + 1, 100000);
        if (shape == 1) a.add(n, 1, 100000);
        a.build();
        for (int i = 0; i < 100000; i++)
        {
            int u = 1 + rng() % n;
            int v = 1 + rng() % n;
            long long edges = abs(u - v);
            if (shape == 1) edges = min<long long>(edges, n - edges);
            if (shape == 2) edges = u == v ? 0 : (u == 1 || v == 1 ? 1 : 2);
            if (a.distance(u, v) != edges * 100000) abort();
        }
        a.build();
    }
    // Chain of triangles: one unit between consecutive articulation points.
    Cactus a(n - 1);
    for (int u = 1; u + 2 < n; u += 2)
    {
        a.add(u, u + 1, 1);
        a.add(u + 1, u + 2, 1);
        a.add(u, u + 2, 1);
    }
    a.build();
    for (int i = 0; i < 100000; i++)
    {
        int u = rng() % (n / 2);
        int v = rng() % (n / 2);
        if (a.distance(2 * u + 1, 2 * v + 1) != abs(u - v)) abort();
    }
    cout << "PASS: 100000-vertex recursive chain/ring/star and 99999-vertex triangle chain; 400000 formula-checked queries\n";
}
