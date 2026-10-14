#include "../src/compact/static_rmq.hpp"
#include <iostream>
#include <random>
#include <cstdlib>
#include <utility>

long long queries = 0;
void require(bool ok)
{
    if (!ok)
    {
        cout << "ORACLE_REJECT\n";
        exit(0);
    }
}

void check(const vector<long long> &a)
{
    StaticRMQ<long long> mn(a);
    StaticRMQ<long long, greater<long long>> mx(a);
#ifdef CPC_WIDA
    WidaRMQ<long long> old_min(a);
    WidaRMQ<long long, greater<long long>> old_max(a);
#endif
    int n = a.size();
    require(mn.a == a && mx.a == a && mn.b >= 1 && mn.b <= 30);
    size_t cells = 0;
    for (const auto &row : mn.st) cells += row.size();
    require(cells <= 2 * a.size());
    for (int l = 0; l < n; l++)
    {
        int low = l, high = l;
        for (int r = l + 1; r <= n; r++)
        {
            if (a[r - 1] < a[low]) low = r - 1;
            if (a[r - 1] > a[high]) high = r - 1;
            require(mn.query(l, r) == low && mx.query(l, r) == high);
#ifdef CPC_WIDA
            require(old_min(l, r) == a[low] && old_max(l, r) == a[high]);
#endif
            queries++;
        }
    }
}

struct Record
{
    long long key;
    int payload;
};

struct ByKey
{
    bool reverse;
    long long *calls;

    bool operator()(const Record &x, const Record &y) const
    {
        (*calls)++;
        return reverse ? x.key > y.key : x.key < y.key;
    }
};

int main()
{
    mt19937_64 rng(276);
    for (int n = 0; n <= 8; n++)
    {
        int total = 1;
        for (int i = 0; i < n; i++) total *= 3;
        for (int code = 0; code < total; code++)
        {
            vector<long long> a(n);
            int value = code;
            for (auto &x : a)
            {
                x = value % 3 - 1;
                value /= 3;
            }
            check(a);
        }
    }
    vector<long long> pool{LLONG_MIN, -1, 0, 1, LLONG_MAX};
    for (int n : {1, 2, 3, 15, 16, 17, 31, 32, 33, 63, 64, 65, 127, 128, 129, 255, 256, 257, 511, 512, 513})
    {
        vector<long long> a(n);
        for (auto &x : a) x = pool[rng() % pool.size()];
        check(a);
        fill(a.begin(), a.end(), 0);
        check(a);
        iota(a.begin(), a.end(), 0);
        check(a);
        reverse(a.begin(), a.end());
        check(a);
    }
    for (int test = 0; test < 200; test++)
    {
        vector<long long> a(rng() % 150);
        for (auto &x : a) x = pool[rng() % pool.size()];
        check(a);
    }
    int n = 500000;
    vector<Record> a(n);
    for (int i = 0; i < n; i++) a[i] = {pool[rng() % pool.size()], i ^ 123};
    for (bool reverse : {false, true})
    {
        long long calls = 0;
        StaticRMQ<Record, ByKey> rmq(a, {reverse, &calls});
        require(calls <= 20LL * n);
        size_t cells = 0;
        for (auto &v : rmq.st) cells += v.size();
        require(cells <= 2 * a.size());
        // Independent iterative segment tree: compare key, then input position.
        int base = 1;
        while (base < n) base *= 2;
        vector<int> tree(2 * base, -1);
        auto pick = [&](int x, int y)
        {
            if (x == -1) return y;
            if (y == -1) return x;
            if (a[x].key == a[y].key) return min(x, y);
            return (reverse ? a[x].key > a[y].key : a[x].key < a[y].key) ? x : y;
        };
        for (int i = 0; i < n; i++) tree[base + i] = i;
        for (int i = base - 1; i; i--) tree[i] = pick(tree[2 * i], tree[2 * i + 1]);
        for (int q = 0; q < 500000; q++)
        {
            int l = rng() % n, r = rng() % n;
            if (l > r) swap(l, r);
            r++;
            int want = -1;
            for (int x = l + base, y = r + base; x < y; x /= 2, y /= 2)
            {
                if (x & 1) want = pick(want, tree[x++]);
                if (y & 1) want = pick(want, tree[--y]);
            }
            long long before = calls;
            int got = rmq.query(l, r);
            require(got == want && calls - before <= 6);
            require(rmq.a[got].payload == a[want].payload);
        }
    }
    cout << "PASS " << queries << " exhaustive/small intervals and 1000000 large segment-tree checks\n";
}
