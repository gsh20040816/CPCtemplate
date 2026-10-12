#include <bits/stdc++.h>
#include <cassert>
using namespace std;
#include "../src/compact/divide_segment_tree.hpp"
namespace original
{
const int inf = 1000000000;
#include "fixtures/wida_lazy/04.cpp"
}
struct Add
{
    int x = 0;
    void apply(Add t)
    {
        x += t.x;
    }
};
struct Info
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
Info operator+(Info a, Info b)
{
    return {min(a.min, b.min), max(a.max, b.max), a.act + b.act, a.sum + b.sum};
}
long long checks = 0;
void check(bool ok)
{
    if (!ok)
        throw runtime_error("mismatch " + to_string(checks));
    checks++;
}
using ll = long long;
int main()
{
    mt19937 rng(458);
    for (int n = 0; n <= 64; n++)
    {
        vector<ll> a(n);
        DivideSegmentTree tree(a);
        for (int iteration = 0; iteration < 2000; iteration++)
        {
            int l = rng() % (n + 1), r = rng() % (n + 1);
            if (l > r)
                swap(l, r);
            int kind = rng() % 3;
            if (kind == 0)
            {
                ll x = rng() % 1000;
                tree.assign(l, r, x);
                fill(a.begin() + l, a.begin() + r, x);
            }
            if (kind == 1)
            {
                ll x = int(rng() % 41) - 20;
                if (l < r)
                    x = max(x, -*min_element(a.begin() + l, a.begin() + r));
                tree.add(l, r, x);
                for (int i = l; i < r; i++)
                    a[i] += x;
            }
            if (kind == 2)
            {
                ll x = 1 + rng() % 15;
                tree.divide(l, r, x);
                for (int i = l; i < r; i++)
                    a[i] /= x;
            }
            check(tree.sum(0, n) == accumulate(a.begin(), a.end(), 0LL));
            int ql = rng() % (n + 1), qr = rng() % (n + 1);
            if (ql > qr)
                swap(ql, qr);
            check(tree.sum(ql, qr) == accumulate(a.begin() + ql, a.begin() + qr, 0LL));
        }
    }
    for (int n = 1; n <= 6; n++)
        for (int code = 0; code < (1 << (2 * n)); code++)
        {
            vector<ll> a(n);
            int value = code;
            for (ll &x : a)
            {
                x = value % 4;
                value /= 4;
            }
            for (int divisor = 1; divisor <= 7; divisor++)
            {
                DivideSegmentTree tree(a);
                tree.divide(0, n, divisor);
                for (int i = 0; i < n; i++)
                    check(tree.sum(i, i + 1) == a[i] / divisor);
            }
        }
    for (int n = 1; n <= 40; n++)
    {
        vector<ll> a(n, 0);
        vector<Info> initial(n, {0, 0, 1, 0});
        original::LazySegmentTree<Info, Add> source(initial);
        DivideSegmentTree tree(a);
        for (int iteration = 0; iteration < 500; iteration++)
        {
            int l = rng() % n, r = l + 1 + rng() % (n - l);
            if (rng() % 2)
            {
                int x = rng() % 100;
                source.rangeApply(l, r, {x});
                tree.add(l, r, x);
                for (int i = l; i < r; i++)
                    a[i] += x;
            }
            else
            {
                source.half();
                tree.divide(0, n, 2);
                for (ll &x : a)
                    x /= 2;
            }
            ll expected = accumulate(a.begin() + l, a.begin() + r, 0LL);
            check(tree.sum(l, r) == expected);
            check(source.rangeQuery(l, r).sum == expected);
        }
    }
    ll bound = DivideSegmentTree::limit;
    DivideSegmentTree edge({0, bound, bound - 1, 1});
    edge.divide(0, 4, LLONG_MAX);
    check(edge.sum(0, 4) == 0);
    edge.assign(0, 4, bound);
    edge.add(1, 3, -bound);
    check(edge.sum(0, 4) == 2 * bound);
    edge.divide(0, 4, 1);
    check(edge.sum(0, 4) == 2 * bound);
    vector<ll> large(500000, bound);
    DivideSegmentTree uniform(large);
    check(uniform.sum(0, 500000) == bound * 500000);
    for (int i = 0; i < 100000; i++)
    {
        uniform.assign(0, 500000, bound);
        uniform.divide(0, 500000, 2);
        uniform.add(0, 500000, -bound / 2);
        check(uniform.sum(0, 500000) == 0);
    }
    for (int i = 0; i < 500000; i++)
        large[i] = (i * 712367821LL) % bound;
    DivideSegmentTree varied(large);
    for (int round = 0; round < 41; round++)
    {
        varied.divide(0, 500000, 2);
        for (ll &x : large)
            x /= 2;
        check(varied.sum(0, 500000) == accumulate(large.begin(), large.end(), 0LL));
    }
    cout << checks << " independent/source/large checks PASS\n";
}
