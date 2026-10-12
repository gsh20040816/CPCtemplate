#include <bits/stdc++.h>
#include <cassert>
using namespace std;
namespace source_add
{
struct Info
{
    int max = -1000000000;
};
Info operator+(Info a, Info b)
{
    return {std::max(a.max, b.max)};
}
#include "fixtures/wida_lazy/03A.cpp"
}
namespace source_lazy
{
const int inf = 1000000000;
#include "fixtures/wida_lazy/04.cpp"
}
#include "../src/compact/lazy_segtree.hpp"

struct Add
{
    int x = 0;
    void apply(Add other)
    {
        x += other.x;
    }
};
struct Summary
{
    int min = 1000000000, max = -1000000000, act = 0;
    long long sum = 0;
    void apply(Add t)
    {
        if (act)
        {
            min += t.x;
            max += t.x;
            sum += 1LL * act * t.x;
        }
    }
};
Summary operator+(Summary a, Summary b)
{
    return {min(a.min, b.min), max(a.max, b.max), a.act + b.act, a.sum + b.sum};
}
Summary op(Summary a, Summary b)
{
    return a + b;
}
Summary summary_identity()
{
    return {};
}
Summary mapping(Add f, Summary x)
{
    x.apply(f);
    return x;
}
Add composition(Add f, Add g)
{
    return {f.x + g.x};
}
Add id()
{
    return {};
}
Summary leaf(int x)
{
    return {x, x, 1, x};
}
long long checks = 0;
void check(bool ok)
{
    if (!ok)
        throw runtime_error("mismatch " + to_string(checks));
    checks++;
}
int main()
{
    mt19937 rng(39363123);
    for (int n = 1; n <= 63; n++)
    {
        vector<int> v(n);
        vector<Summary> initial(n);
        source_add::SegmentTree a(n);
        for (int i = 0; i < n; i++)
        {
            v[i] = rng() % 100;
            initial[i] = leaf(v[i]);
            a.modify(i, {v[i]});
        }
        source_lazy::LazySegmentTree<Summary, Add> b(initial);
        lazy_segtree<Summary, Add, op, summary_identity, mapping, composition, id> c(initial);
        for (int t = 0; t < 1200; t++)
        {
            int l = rng() % (n + 1), r = rng() % (n + 1);
            if (l > r)
                swap(l, r);
            if (rng() % 3 == 0)
            {
                int p = rng() % n;
                v[p] = rng() % 100;
                a.modify(p, {v[p]});
                b.modify(p, leaf(v[p]));
                c.set(p, leaf(v[p]));
            }
            else
            {
                int delta = int(rng() % 21) - 10;
                a.rangeAdd(l, r, delta);
                b.rangeApply(l, r, {delta});
                c.apply(l, r, {delta});
                for (int i = l; i < r; i++)
                    v[i] += delta;
            }
            Summary truth;
            int first = -1, last = -1;
            int threshold = int(rng() % 151) - 25;
            for (int i = l; i < r; i++)
            {
                truth = truth + leaf(v[i]);
                if (v[i] >= threshold)
                {
                    if (first == -1)
                        first = i;
                    last = i;
                }
            }
            auto old = b.rangeQuery(l, r), now = c.prod(l, r);
            check(a.query(l, r).max == truth.max);
            check(old.min == truth.min && old.max == truth.max && old.sum == truth.sum && old.act == truth.act);
            check(now.min == truth.min && now.max == truth.max && now.sum == truth.sum && now.act == truth.act);
            auto pred = [&](Summary s)
            {
                return s.max >= threshold;
            };
            auto ok = [&](Summary s)
            {
                return s.max < threshold;
            };
            check(b.findFirst(l, r, pred) == first);
            check(b.findLast(l, r, pred) == last);
            int x = c.max_right(l, ok), y = c.min_left(r, ok) - 1;
            check((x < r ? x : -1) == first);
            check((y >= l ? y : -1) == last);
        }
    }
    cout << "general operations " << checks << '\n';
    // Source-only half audit: all leaves active and values nonnegative.
    for (int n = 1; n <= 6; n++)
    {
        int states = 1 << (2 * n);
        for (int code = 0; code < states; code++)
        {
            vector<Summary> initial(n);
            vector<int> v(n);
            int digits = code;
            for (int i = 0; i < n; i++)
            {
                v[i] = digits % 4;
                digits /= 4;
                initial[i] = leaf(v[i]);
            }
            source_lazy::LazySegmentTree<Summary, Add> tree(initial);
            for (int iteration = 0; iteration < 4; iteration++)
            {
                tree.half();
                for (int i = 0; i < n; i++)
                {
                    v[i] /= 2;
                    check(tree.rangeQuery(i, i + 1).sum == v[i]);
                }
            }
        }
    }
    cout << checks << " checks PASS; half is source-only, maintainL/R not instantiated\n";
}
