#include "../src/compact/tree_block_distinct.hpp"
#include <chrono>
#include <random>

int main()
{
    const int n = 40000;
    const int q = 100000;
    mt19937 rng(6177);
    for (string shape : {"chain-unique", "chain-periodic", "star", "binary"})
    {
        auto start = chrono::steady_clock::now();
        TreeBlockDistinct g(n);
        vector<long long> colors(n + 1);
        for (int u = 1; u <= n; u++)
        {
            colors[u] = shape == "chain-periodic" ? u % 997 : u;
            if (u > 1)
            {
                int p = shape == "star" ? 1 : shape == "binary" ? u / 2 : u - 1;
                g.add(p, u);
            }
        }
        g.build(colors);
        int last = 0;
        long long checksum = 0;
        for (int i = 0; i < q; i++)
        {
            int u = 1 + rng() % n;
            int v = 1 + rng() % n;
            int encoded = u ^ last;
            int want;
            if (shape == "star")
                want = u == v ? 1 : (u == 1 || v == 1 ? 2 : 3);
            else if (shape == "binary")
            {
                int a = u;
                int b = v;
                want = 1;
                while (a != b)
                {
                    if (a > b) a /= 2;
                    else b /= 2;
                    want++;
                }
            }
            else
            {
                want = abs(u - v) + 1;
                if (shape == "chain-periodic") want = min(want, 997);
            }
            last = g.query(encoded ^ last, v);
            if (last != want) abort();
            checksum += last;
        }
        auto elapsed = chrono::duration<double>(chrono::steady_clock::now() - start).count();
        cout << shape << " n=" << n << " q=" << q << " keys=" << g.k
             << " checksum=" << checksum << " seconds=" << elapsed << '\n';
    }
}
