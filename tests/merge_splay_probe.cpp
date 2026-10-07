#include <bits/stdc++.h>
#include "../src/compact/merge_splay.hpp"
using namespace std;
using ll = long long;
long long checks = 0, cases = 0;

void require(bool ok)
{
    checks++;
    if (!ok)
    {
        cout << "ORACLE_REJECT\n";
        exit(0);
    }
}

int walk(MergeSplay &t, int x, int p, vector<int> &seen, vector<int> &order)
{
    if (!x) return 0;
    require(0 < x && x <= t.n && !seen[x]);
    seen[x] = 1;
    require(t.a[x].fa == p);
    int l = walk(t, t.a[x].ch[0], x, seen, order);
    order.push_back(x - 1);
    int r = walk(t, t.a[x].ch[1], x, seen, order);
    require(t.a[x].siz == l + r + 1);
    return l + r + 1;
}

vector<int> group(const vector<int> &label, const vector<ll> &val, int u)
{
    vector<int> ids;
    for (int i = 0; i < (int)label.size(); i++)
        if (label[i] == label[u]) ids.push_back(i);
    sort(ids.begin(), ids.end(), [&](int x, int y)
    {
        return pair{val[x], x} < pair{val[y], y};
    });
    return ids;
}

void verify(MergeSplay &t, const vector<int> &label, const vector<ll> &val)
{
    require(t.a.size() == val.size() + 1);
    vector<int> seen(t.n + 1);
    for (int x = 1; x <= t.n; x++)
        if (!t.a[x].fa)
        {
            vector<int> order;
            walk(t, x, 0, seen, order);
            require(order == group(label, val, x - 1));
        }
    for (int x = 1; x <= t.n; x++) require(seen[x]);
    for (int u = 0; u < t.n; u++)
    {
        auto ids = group(label, val, u);
        require(t.value(u) == val[u]);
        require(t.size(u) == (int)ids.size());
        require(t.rank(u) == find(ids.begin(), ids.end(), u) - ids.begin() + 1);
        for (int k = 1; k <= (int)ids.size(); k++)
            require(t.kth(u, k) == optional<int>(ids[k - 1]));
        for (ll k : {LLONG_MIN, 0LL, (ll)ids.size() + 1, LLONG_MAX})
            require(!t.kth(u, k));
        for (int v = 0; v < t.n; v++)
            require(t.same(u, v) == (label[u] == label[v]));
    }
}

void join(vector<int> &label, int u, int v)
{
    int x = label[u], y = label[v];
    for (auto &a : label)
        if (a == y) a = x;
}

void one_case(const vector<int> &label, const vector<ll> &val)
{
    int n = val.size();
    MergeSplay base(val);
    for (int u = n - 1; u >= 0; u--)
        for (int v = u + 1; v < n; v++)
            if (label[u] == label[v]) base.merge(u, v);
    verify(base, label, val);
    for (int u = 0; u < n; u++)
    {
        for (int v = 0; v < n; v++)
        {
            auto t = base;
            auto next = label;
            bool changed = label[u] != label[v];
            require(t.merge(u, v) == changed);
            join(next, u, v);
            verify(t, next, val);
            require(!t.merge(v, u));
            cases++;
        }
        for (ll value : {LLONG_MIN, -1LL, 0LL, LLONG_MAX})
        {
            auto t = base;
            auto values = val;
            values[u] = value;
            t.set(u, value);
            verify(t, label, values);
            t.set(u, value);
            verify(t, label, values);
            cases++;
        }
    }
    // No nodes, values or parent pointers shared across copies.
    verify(base, label, val);
}

int main(int argc, char **)
{
    MergeSplay empty(vector<ll>{});
    verify(empty, {}, {});
    for (int n = 1; n <= 6; n++)
    {
        vector<int> label(n);
        function<void(int,int)> partitions = [&](int i, int high)
        {
            if (i == n)
            {
                int ways = n <= 4 ? (int)pow(3, n) : 4;
                for (int mask = 0; mask < ways; mask++)
                {
                    vector<ll> val(n);
                    int code = mask;
                    for (int u = 0; u < n; u++)
                    {
                        if (n <= 4)
                        {
                            val[u] = code % 3 - 1;
                            code /= 3;
                        }
                        else
                        {
                            val[u] = mask == 0 ? 0 : mask == 1 ? u : mask == 2 ? -u : u % 2 ? LLONG_MIN : LLONG_MAX;
                        }
                    }
                    one_case(label, val);
                }
                return;
            }
            for (int x = 0; x <= high + 1; x++)
            {
                label[i] = x;
                partitions(i + 1, max(high, x));
            }
        };
        label[0] = 0;
        partitions(1, 0);
    }
    mt19937 rng(14793224);
    for (int test = 0; test < 100; test++)
    {
        int n = 1 + rng() % 40;
        vector<int> label(n);
        iota(label.begin(), label.end(), 0);
        vector<ll> val(n);
        MergeSplay t(val);
        for (int step = 0; step < 300; step++)
        {
            int u = rng() % n, v = rng() % n;
            if (step % 3 == 0)
            {
                require(t.merge(u, v) == (label[u] != label[v]));
                join(label, u, v);
            }
            else
            {
                val[u] = step % 7 == 0 ? LLONG_MIN : step % 7 == 1 ? LLONG_MAX : (int)(rng() % 11) - 5;
                t.set(u, val[u]);
            }
            verify(t, label, val);
        }
        cases++;
    }
    cout << "SMALL " << cases << " cases " << checks << " checks\n";
    if (argc > 1) return 0;
    int n = 100000;
    vector<ll> val(n);
    MergeSplay t(val);
    for (int begin : {0, n / 2})
    {
        for (int u = begin + 1; u < begin + n / 2; u++) require(t.merge(begin, u));
        for (int k = 1; k <= n / 2; k++) require(t.kth(begin, k) == optional<int>(begin + k - 1));
    }
    require(t.merge(0, n / 2));
    for (int k = 1; k <= n; k++) require(t.kth(0, k) == optional<int>(k - 1));
    for (int u = 0; u < n; u++)
    {
        t.set(u, LLONG_MIN);
        require(t.kth(0, 1) == optional<int>(u));
        require(t.rank(u) == 1);
        t.set(u, LLONG_MAX);
        require(t.kth(0, n) == optional<int>(u));
        t.set(u, 0);
        require(t.size(u) == n);
        require(t.a.size() == (size_t)n + 1);
    }
    // Balanced union schedule exercises O(log n) moves per element.
    MergeSplay balanced(val);
    for (int width = 1; width < n; width *= 2)
        for (int u = 0; u + width < n; u += 2 * width)
            require(balanced.merge(u, u + width));
    for (int k = 1; k <= n; k++) require(balanced.kth(0, k) == optional<int>(k - 1));
    cout << "PASS " << cases << " cases " << checks << " checks\n";
}
