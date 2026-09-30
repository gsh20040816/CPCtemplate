#include "../../src/compact/kth_residue.hpp"
#include "../../src/compact/composite_roots.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    PollardRho rho;
    while (t--)
    {
        unsigned long long n;
        long long m, k;
        cin >> n >> m >> k;
        auto f = root_factors(m, rho);
        vector<long long> a;
        if (f.size() == 1)
        {
            auto [p, e, g] = f[0];
            if (e == 1)
            {
                auto r = KthResidue::solve(k, n, p, p == 2 ? 1 : g);
                if (r)
                {
                    long long x = r->first;
                    for (long long i = 0; i < r->count; i++)
                    {
                        a.push_back(x);
                        x = (__int128)x * r->ratio % p;
                    }
                }
            }
            else
            {
                auto r = PrimePowerRoots::solve(k, n, p, e, g);
                if (r)
                    for (long long i = 0; i < r->count[0]; i++)
                        for (long long j = 0; j < r->count[1]; j++)
                            for (long long z = 0; z < r->lifts; z++)
                                a.push_back(r->get(i, j, z));
            }
        }
        else
        {
            auto r = CompositeRoots::solve(k, n, f);
            if (r)
                for (long long i = 0; i < r->total; i++) a.push_back(r->get(i));
        }
        sort(a.begin(), a.end());
        cout << a.size() << '\n';
        if (!a.empty())
        {
            for (int i = 0; i < (int)a.size(); i++)
                cout << a[i] << (i + 1 == (int)a.size() ? '\n' : ' ');
        }
    }
    return 0;
}
