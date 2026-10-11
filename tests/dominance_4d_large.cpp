#include "../src/compact/dominance_4d.hpp"
#include "../src/compact/dominance_3d.hpp"
#include <chrono>
#include <random>

int main()
{
    const int n = 100000;
    mt19937 rng(21566);
    for (string shape : {"chain", "antichain", "duplicates", "random-3d"})
    {
        vector<array<long long, 4>> p(n);
        vector<int> y(n), z(n);
        iota(y.begin(), y.end(), 0);
        iota(z.begin(), z.end(), 0);
        shuffle(y.begin(), y.end(), rng);
        shuffle(z.begin(), z.end(), rng);
        for (int i = 0; i < n; i++)
        {
            if (shape == "chain") p[i] = {i, i, i, i};
            if (shape == "antichain") p[i] = {i, i, i, -i};
            if (shape == "duplicates") p[i] = {7, 7, 7, 7};
            if (shape == "random-3d") p[i] = {i, y[i], z[i], i};
        }
        for (bool strict : {false, true})
        {
            vector<int> want(n);
            if (shape == "chain") iota(want.begin(), want.end(), 0);
            if (shape == "duplicates" && !strict) fill(want.begin(), want.end(), n - 1);
            if (shape == "random-3d")
            {
                vector<array<long long, 3>> q(n);
                for (int i = 0; i < n; i++) q[i] = {p[i][0], p[i][1], p[i][2]};
                want = Dominance3D::count(q);
            }
            auto start = chrono::steady_clock::now();
            auto ans = Dominance4D::count(p, strict);
            if (ans != want) abort();
            auto elapsed = chrono::duration<double>(chrono::steady_clock::now() - start).count();
            cout << shape << " strict=" << strict << " n=" << n
                 << " checksum=" << accumulate(ans.begin(), ans.end(), 0LL)
                 << " seconds=" << elapsed << '\n';
        }
    }
}
