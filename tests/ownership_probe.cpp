#include "../src/compact/persistent_dsu.hpp"
#include "../src/compact/merge_split_tree.hpp"
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
using namespace std;
using ll = long long;
long long checks = 0;
int cases = 0;

void require(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle");
}

void persistent()
{
    mt19937 gen(3402);
    for (int n = 1; n <= 32; n++)
    {
        cases++;
        PersistentDSU d(n);
        vector<vector<int>> labels(1, vector<int>(n));
        iota(labels[0].begin(), labels[0].end(), 0);
        for (int step = 0; step < 220; step++)
        {
            int v = step % 2 ? step : gen() % labels.size();
            int x = gen() % n, y = gen() % n;
            auto old = d.t;
            auto a = labels[v];
            int id;
            if (step % 7 == 0)
                id = d.copy(v);
            else
            {
                id = d.merge(v, x, y);
                int from = a[x], to = a[y];
                for (int &z : a)
                    if (z == from) z = to;
            }
            require(id == (int)labels.size());
            if (step % 7 == 0 || labels[v][x] == labels[v][y])
                require(d.t.size() == old.size());
            labels.push_back(a);
            for (int i = 0; i < (int)old.size(); i++)
                require(old[i].l == d.t[i].l && old[i].r == d.t[i].r && old[i].v == d.t[i].v);
            auto count = d.t.size();
            auto roots = d.root;
            for (int ver : {v, id, (int)(gen() % labels.size()), 0})
                for (int i = 0; i < n; i++)
                {
                    int sz = 0;
                    for (int j = 0; j < n; j++)
                    {
                        require(d.same(ver, i, j) == (labels[ver][i] == labels[ver][j]));
                        sz += labels[ver][i] == labels[ver][j];
                    }
                    require(d.size(ver, i) == sz);
                    int p = i, depth = 0;
                    while (d.get(d.root[ver], 0, n, p) >= 0)
                    {
                        p = d.get(d.root[ver], 0, n, p);
                        depth++;
                        require(depth <= 5);
                    }
                    require((1LL << depth) <= sz);
                    require(p == d.find(ver, i));
                }
            require(count == d.t.size() && roots == d.root);
        }
        auto clone = d;
        clone.merge(0, 0, n - 1);
        require(d.root.size() == labels.size());
    }
    cases++;
    PersistentDSU d(4);
    int a = d.merge(0, 1, 0);
    require(d.find(a, 1) == 0);
    int b = d.merge(a, 0, 2);
    require(d.find(b, 2) == 0 && d.size(b, 2) == 3);
    int c = d.merge(a, 2, 3);
    require(!d.same(c, 0, 2) && !d.same(0, 1, 0));
    // Adversarial sequential unions must stay shallow after balancing.
    PersistentDSU big(100000);
    for (int i = 1; i < big.n; i++) big.merge(i - 1, 0, i);
    for (int i = 0; i < big.n; i++)
    {
        require(big.size(99999, i) == 100000);
        int p = big.get(big.root.back(), 0, big.n, i);
        require(p < 0 || big.get(big.root.back(), 0, big.n, p) < 0);
    }
}

ll audit_node(const MergeSplitTree &s, int p, int l, int r, vector<int> &seen)
{
    if (!p) return 0;
    require(p > 0 && p < (int)s.t.size());
    require(!seen[p]);
    seen[p] = 1;
    auto a = s.t[p];
    require(a.sum > 0);
    if (r - l == 1)
        require(!a.l && !a.r);
    else
    {
        int m = l + (r - l) / 2;
        ll x = audit_node(s, a.l, l, m, seen);
        ll y = audit_node(s, a.r, m, r, seen);
        require((__int128)x + y == a.sum);
    }
    return a.sum;
}

void audit(const MergeSplitTree &s, const vector<vector<ll>> &a, bool exhaustive)
{
    require(a.size() == s.root.size());
    require(s.t[0].sum == 0 && s.t[0].l == 0 && s.t[0].r == 0);
    vector<int> seen(s.t.size());
    for (int id = 0; id < (int)a.size(); id++)
    {
        ll total = accumulate(a[id].begin(), a[id].end(), 0LL);
        require(audit_node(s, s.root[id], 0, s.n, seen) == total);
        require(s.kth(id, 0) == -1 && s.kth(id, -1) == -1);
        if (total < LLONG_MAX) require(s.kth(id, total + 1) == -1);
        ll pre = 0;
        for (int x = 0; x < s.n; x++)
        {
            if (a[id][x])
            {
                require(s.kth(id, pre + 1) == x);
                require(s.kth(id, pre + a[id][x]) == x);
            }
            pre += a[id][x];
            require(s.sum(id, x, x + 1) == a[id][x]);
        }
        if (exhaustive)
            for (int l = 0; l <= s.n; l++)
            {
                ll want = 0;
                for (int r = l; r <= s.n; r++)
                {
                    require(s.sum(id, l, r) == want);
                    if (r < s.n) want += a[id][r];
                }
            }
    }
    for (int p : s.free)
    {
        require(p > 0 && p < (int)s.t.size() && !seen[p]);
        seen[p] = 1;
        require(!s.t[p].l && !s.t[p].r && !s.t[p].sum);
    }
    for (int p = 1; p < (int)s.t.size(); p++) require(seen[p] == 1);
}

void mutable_sets()
{
    mt19937 gen(5494);
    for (int n = 1; n <= 5; n++)
    {
        int limit = 1;
        for (int i = 0; i < n; i++) limit *= 3;
        for (int mask = 0; mask < limit; mask++)
        {
            cases++;
            vector<ll> a(n);
            int m = mask;
            for (ll &x : a)
            {
                x = m % 3;
                m /= 3;
            }
            MergeSplitTree base(a);
            for (int l = 0; l <= n; l++)
                for (int r = l; r <= n; r++)
                {
                    auto s = base;
                    vector<vector<ll>> want{a, vector<ll>(n)};
                    for (int i = l; i < r; i++)
                    {
                        want[1][i] = want[0][i];
                        want[0][i] = 0;
                    }
                    require(s.split(0, l, r) == 1);
                    audit(s, want, true);
                    s.merge(0, 1);
                    audit(s, {a, vector<ll>(n)}, true);
                }
            audit(base, {a}, true);
        }
    }
    for (int n = 1; n <= 24; n++)
    {
        cases++;
        MergeSplitTree s(n);
        vector<vector<ll>> a(1, vector<ll>(n));
        for (int step = 0; step < 400; step++)
        {
            int id = gen() % a.size();
            int x = gen() % n;
            int op = gen() % 3;
            if (op == 0)
            {
                ll delta = (gen() % 2) ? (ll)(gen() % 20) : -a[id][x];
                s.add(id, x, delta);
                a[id][x] += delta;
            }
            else if (op == 1)
            {
                int l = gen() % (n + 1), r = gen() % (n + 1);
                if (l > r) swap(l, r);
                vector<ll> b(n);
                for (int i = l; i < r; i++)
                {
                    b[i] = a[id][i];
                    a[id][i] = 0;
                }
                require(s.split(id, l, r) == (int)a.size());
                a.push_back(b);
            }
            else if (a.size() > 1)
            {
                int other = gen() % a.size();
                if (other == id) other = (other + 1) % a.size();
                s.merge(id, other);
                for (int i = 0; i < n; i++)
                {
                    a[id][i] += a[other][i];
                    a[other][i] = 0;
                }
            }
            audit(s, a, step % 31 == 0);
            if (step % 61 == 0)
            {
                auto clone = s;
                clone.add(id, x, 3);
                audit(s, a, true);
            }
        }
    }
    cases++;
    MergeSplitTree s(vector<ll>{LLONG_MAX - 1, 1, 0});
    audit(s, {{LLONG_MAX - 1, 1, 0}}, true);
    s.split(0, 0, 1);
    audit(s, {{0, 1, 0}, {LLONG_MAX - 1, 0, 0}}, true);
    s.merge(1, 0);
    s.add(1, 0, -(LLONG_MAX - 1));
    s.add(1, 1, -1);
    audit(s, {vector<ll>(3), vector<ll>(3)}, true);
    auto allocated = s.t.size();
    for (int i = 0; i < 10000; i++)
    {
        s.add(0, 2, LLONG_MAX);
        s.merge(1, 0);
        s.add(1, 2, -LLONG_MAX);
    }
    require(s.t.size() <= allocated);
    audit(s, {vector<ll>(3), vector<ll>(3)}, true);
}

int main()
{
    try
    {
        persistent();
        mutable_sets();
        cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
