#include "../src/compact/kd_min.hpp"
#include <iostream>
#include <random>
#include <cstdlib>

void require(bool ok)
{
    if (!ok)
    {
        cout << "ORACLE_REJECT\n";
        exit(0);
    }
}

int audit(const KDMin &kd, int u, int fa, int depth)
{
    if (u == -1) return -1;
    require(depth <= 20 && kd.a[u].fa == fa);
    int best = kd.a[u].alive ? u : -1;
    auto low = kd.p[u].p, high = low;
    for (int v : kd.a[u].ch)
    {
        int next = audit(kd, v, u, depth + 1);
        if (next != -1 && (best == -1 || make_pair(kd.p[next].key, next) < make_pair(kd.p[best].key, best))) best = next;
        if (v == -1) continue;
        for (int d = 0; d < 2; d++)
        {
            low[d] = min(low[d], kd.a[v].low[d]);
            high[d] = max(high[d], kd.a[v].high[d]);
        }
    }
    require(kd.a[u].best == best && kd.a[u].low == low && kd.a[u].high == high);
    return best;
}

int main()
{
    mt19937_64 rng(44);
    vector<long long> pool{LLONG_MIN, -2, -1, 0, 1, 2, LLONG_MAX};
    long long queries = 0;
    for (int test = 0; test < 1000; test++)
    {
        int n = test % 70;
        vector<KDMin::Item> p(n);
        vector<bool> alive(n, true);
        for (auto &v : p) v = {{pool[rng() % pool.size()], pool[rng() % pool.size()]}, pool[rng() % pool.size()]};
        KDMin kd(p);
        for (int i = 0; i < n; i++) require(kd.p[i].p == p[i].p && kd.p[i].key == p[i].key);
        for (int step = 0; step < 150; step++)
        {
            if (n && step % 3 == 0)
            {
                int id = rng() % n;
                kd.erase(id);
                alive[id] = false;
            }
            KDMin::Point low, high;
            for (int d = 0; d < 2; d++)
            {
                low[d] = pool[rng() % pool.size()];
                high[d] = pool[rng() % pool.size()];
                if (step % 3 && low[d] > high[d]) swap(low[d], high[d]);
            }
            int want = -1;
            for (int i = 0; i < n; i++)
            {
                if (!alive[i] || p[i].p[0] < low[0] || p[i].p[0] > high[0] || p[i].p[1] < low[1] || p[i].p[1] > high[1]) continue;
                if (want == -1 || make_pair(p[i].key, i) < make_pair(p[want].key, want)) want = i;
            }
            require(kd.query(low, high) == want);
            audit(kd, kd.root, -1, 0);
            queries++;
        }
        auto copy = kd;
        for (int i = 0; i < n; i++) copy.erase(i);
        require(copy.query({LLONG_MIN, LLONG_MIN}, {LLONG_MAX, LLONG_MAX}) == -1);
        audit(kd, kd.root, -1, 0);
    }
    int n = 100000;
    for (bool duplicate : {false, true})
    {
        vector<KDMin::Item> p(n);
        for (int i = 0; i < n; i++) p[i] = {{duplicate ? 0 : i % 1000, duplicate ? 0 : i / 1000}, n - i};
        KDMin kd(p);
        audit(kd, kd.root, -1, 0);
        for (int i = n - 1; i >= 0; i--)
        {
            require(kd.query({LLONG_MIN, LLONG_MIN}, {LLONG_MAX, LLONG_MAX}) == i);
            if (!duplicate) require(kd.query(p[i].p, p[i].p) == i);
            kd.erase(i);
            kd.erase(i);
        }
        require(kd.query({LLONG_MIN, LLONG_MIN}, {LLONG_MAX, LLONG_MAX}) == -1);
        audit(kd, kd.root, -1, 0);
    }
    cout << "PASS " << queries << " independent rectangle queries, invariants and two 100000-point deletion families\n";
}
