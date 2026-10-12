#include <bits/stdc++.h>
#include <cassert>
using namespace std;
namespace old_bit
{
#include "fixtures/wida_basic_ds/01A.cpp"
}
namespace new_bit
{
#include "fixtures/wida_basic_ds/01B.cpp"
}
namespace plain_dsu
{
#include "fixtures/wida_basic_ds/02A.cpp"
}
namespace rollback_dsu
{
#include "fixtures/wida_basic_ds/02B.cpp"
}
namespace search_tree
{
#include "fixtures/wida_basic_ds/03C.cpp"
}
namespace merge_tree
{
#include "fixtures/wida_basic_ds/03D.cpp"
}
#include "../src/compact/data_structure.hpp"
#include "../src/compact/segtree.hpp"

long long checks = 0;
void check(bool ok)
{
    if (!ok)
        throw runtime_error("mismatch at check " + to_string(checks));
    checks++;
}

struct MaxInfo
{
    int value = INT_MIN;
};
MaxInfo operator+(MaxInfo a, MaxInfo b)
{
    return {max(a.value, b.value)};
}
MaxInfo max_op(MaxInfo a, MaxInfo b)
{
    return a + b;
}
MaxInfo max_e()
{
    return {};
}
string join(string a, string b)
{
    return a + b;
}
string empty_string()
{
    return {};
}
struct Join
{
    string operator()(const string &a, const string &b) const
    {
        return a + b;
    }
};

void fenwick_checks()
{
    for (int n = 1; n <= 6; n++)
    {
        int states = 1 << (2 * n);
        for (int code = 0; code < states; code++)
        {
            old_bit::Fenwick<long long> a(n);
            new_bit::Fenwick<long long> b(n);
            Fenwick<long long> c(n);
            vector<int> v(n);
            int digits = code;
            for (int i = 0; i < n; i++)
            {
                v[i] = digits % 4;
                digits /= 4;
                a.add(i, v[i]);
                b.add(i, v[i]);
                c.add(i + 1, v[i]);
            }
            for (int l = 0; l <= n; l++)
                for (int r = l; r <= n; r++)
                {
                    long long sum = accumulate(v.begin() + l, v.begin() + r, 0LL);
                    check(a.rangeSum(l, r) == sum);
                    check(b.rangeSum(l, r) == sum);
                    check(c.query(l + 1, r) == sum);
                }
            int total = accumulate(v.begin(), v.end(), 0);
            for (int k = 0; k <= total + 1; k++)
            {
                int x = 0, sum = 0;
                while (x < n && sum + v[x] <= k)
                    sum += v[x++];
                check(a.kth(k) == x);
                check(b.select(k) == x);
                check(c.kth(k + 1) == x + 1);
            }
            a.init(n);
            b.init(n);
            check(a.sum(n) == 0 && b.sum(n) == 0);
        }
    }
    Fenwick<long long> empty;
    check(empty.sum(0) == 0 && empty.kth(1) == 1);
    old_bit::Fenwick<long long> old_empty;
    new_bit::Fenwick<long long> new_empty;
    check(old_empty.sum(0) == 0 && new_empty.sum(0) == 0);
    mt19937 rng(63382128);
    old_bit::Fenwick<long long> a(31);
    new_bit::Fenwick<long long> b(31);
    Fenwick<long long> c(31);
    vector<long long> v(31);
    for (int t = 0; t < 5000; t++)
    {
        int p = rng() % 31;
        int delta = int(rng() % 21) - 10;
        v[p] += delta;
        a.add(p, delta);
        b.add(p, delta);
        c.add(p + 1, delta);
        int l = rng() % 32, r = rng() % 32;
        if (l > r)
            swap(l, r);
        long long sum = accumulate(v.begin() + l, v.begin() + r, 0LL);
        check(a.rangeSum(l, r) == sum && b.rangeSum(l, r) == sum);
        check(c.query(l + 1, r) == sum);
    }
}

bool relabel(vector<int> &label, int x, int y)
{
    int from = label[y], to = label[x];
    if (from == to)
        return false;
    for (int &v : label)
        if (v == from)
            v = to;
    return true;
}
void dsu_checks()
{
    mt19937 rng(569639);
    for (int n = 1; n <= 25; n++)
    {
        plain_dsu::DSU a(n);
        dsu b(n);
        vector<int> label(n);
        iota(label.begin(), label.end(), 0);
        for (int t = 0; t < 100; t++)
        {
            int x = rng() % n, y = rng() % n;
            bool changed = relabel(label, x, y);
            check(a.merge(x, y) == changed && b.merge(x, y) == changed);
            for (int i = 0; i < n; i++)
            {
                int size = count(label.begin(), label.end(), label[i]);
                check(a.size(i) == size && b.size(i) == size);
                for (int j = 0; j < n; j++)
                    check(a.same(i, j) == (label[i] == label[j]) && b.same(i, j) == (label[i] == label[j]));
            }
        }
        a.init(n);
        for (int i = 0; i < n; i++)
            check(a.size(i) == 1);

        rollback_dsu::DSU c(n);
        RollbackDSU d(n);
        // Both rollback implementations expose vertices 0 through n.
        vector<int> initial(n + 1);
        iota(initial.begin(), initial.end(), 0);
        vector<vector<int>> history{initial};
        for (int t = 0; t < 600; t++)
        {
            if (rng() % 3 == 0)
            {
                int stamp = rng() % history.size();
                c.revert(stamp);
                d.rollback(stamp);
                history.resize(stamp + 1);
            }
            else
            {
                int x = rng() % (n + 1), y = rng() % (n + 1);
                auto next = history.back();
                bool changed = relabel(next, x, y);
                check(c.merge(x, y) == changed && d.merge(x, y) == changed);
                if (changed)
                    history.push_back(next);
            }
            check(c.time() == int(history.size()) - 1 && d.snapshot() == c.time());
            const auto &v = history.back();
            for (int i = 0; i <= n; i++)
            {
                int size = count(v.begin(), v.end(), v[i]);
                check(c.siz[c.find(i)] == size && d.siz[d.find(i)] == size);
                for (int j = 0; j <= n; j++)
                    check((c.find(i) == c.find(j)) == (v[i] == v[j]) && (d.find(i) == d.find(j)) == (v[i] == v[j]));
            }
        }
    }
}

void segment_checks()
{
    mt19937 rng(267353839);
    for (int n = 1; n <= 33; n++)
    {
        vector<MaxInfo> v(n);
        for (auto &x : v)
            x.value = int(rng() % 21) - 10;
        search_tree::SegmentTree<MaxInfo> a(v);
        segtree<MaxInfo, max_op, max_e> b(v);
        vector<string> text(n);
        for (int i = 0; i < n; i++)
            text[i] = string(1, 'a' + i % 26);
        merge_tree::SegmentTree<string, Join> c(text);
        segtree<string, join, empty_string> d(text);
        for (int t = 0; t < 600; t++)
        {
            int p = rng() % n;
            v[p].value = int(rng() % 21) - 10;
            a.modify(p, v[p]);
            b.set(p, v[p]);
            text[p] = string(rng() % 3, 'a' + rng() % 26);
            c.modify(p, text[p]);
            d.set(p, text[p]);
            int l = rng() % (n + 1), r = rng() % (n + 1);
            if (l > r)
                swap(l, r);
            int threshold = int(rng() % 25) - 12;
            int maximum = INT_MIN, first = -1, last = -1;
            string joined;
            for (int i = l; i < r; i++)
            {
                maximum = max(maximum, v[i].value);
                joined += text[i];
                if (v[i].value >= threshold)
                {
                    if (first == -1)
                        first = i;
                    last = i;
                }
            }
            check(a.rangeQuery(l, r).value == maximum && b.prod(l, r).value == maximum);
            check(c.rangeQuery(l, r) == joined && d.prod(l, r) == joined);
            auto pred = [&](MaxInfo x)
            {
                return x.value >= threshold;
            };
            auto ok = [&](MaxInfo x)
            {
                return x.value < threshold;
            };
            check(a.findFirst(l, r, pred) == first);
            check(a.findLast(l, r, pred) == last);
            int left = b.max_right(l, ok);
            int right = b.min_left(r, ok) - 1;
            check((left < r ? left : -1) == first);
            check((right >= l ? right : -1) == last);
        }
        a.init(n, MaxInfo{7});
        check(a.rangeQuery(0, n).value == 7);
        merge_tree::SegmentTree<string, Join> blank(n);
        check(blank.rangeQuery(0, n).empty());
    }
    segtree<MaxInfo, max_op, max_e> empty;
    check(empty.prod(0, 0).value == INT_MIN);
}

int main(int argc, char **argv)
{
    string task = argc > 1 ? argv[1] : "normal";
    if (task == "empty-old")
    {
        old_bit::Fenwick<int> bit;
        cout << bit.kth(0) << '\n';
        return 0;
    }
    if (task == "empty-new")
    {
        new_bit::Fenwick<int> bit;
        cout << bit.select(0) << '\n';
        return 0;
    }
    fenwick_checks();
    cout << "fenwick " << checks << '\n';
    dsu_checks();
    cout << "through dsu " << checks << '\n';
    segment_checks();
    cout << checks << " independent checks PASS\n";
}
