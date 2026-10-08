#include "../src/compact/overall_kth.hpp"

void need(bool ok)
{
    if (!ok) abort();
}

int main()
{
    mt19937 rng(3562617);
    vector<long long> pool{LLONG_MIN, LLONG_MAX, -1, 0, 1, 7};
    for (int t = 0; t < 2000; t++)
    {
        int n = 1 + rng() % 35;
        vector<long long> a(n);
        for (auto &x : a) x = pool[rng() % pool.size()];
        OverallKth solver(a);
        need(solver.run().empty());
        vector<long long> want;
        for (int i = 0; i < 100; i++)
        {
            if (rng() % 2)
            {
                int pos = rng() % n;
                long long value = pool[rng() % pool.size()];
                a[pos] = value;
                solver.set(pos + 1, value);
            }
            else
            {
                int l = rng() % n, r = rng() % n;
                if (l > r) swap(l, r);
                int k = 1 + rng() % (r - l + 1);
                vector<long long> b(a.begin() + l, a.begin() + r + 1);
                sort(b.begin(), b.end());
                need(solver.query(l + 1, r + 1, k) == int(want.size()));
                want.push_back(b[k - 1]);
            }
            if (i % 17 == 0) need(solver.run() == want);
        }
        need(solver.run() == want);
        need(solver.run() == want);
    }
    cout << "PASS 2000 operation streams, repeated and incremental run\n";
}
