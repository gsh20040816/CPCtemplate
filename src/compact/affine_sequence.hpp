#pragma once
#include <algorithm>
#include <cassert>
#include <random>
#include <vector>
#include "number_theory.hpp"
using namespace std;

template <int mod = 998244353> struct AffineSequenceTreap
{
    static_assert(mod > 0);
    using Z = ModInt<mod>;

    struct Node
    {
        int l = 0, r = 0, siz = 0;
        Z val = 0, sum = 0, mul = 1, add = 0;
        unsigned long long pri = 0;
        bool rev = false;
    };

    vector<Node> a{Node{}};
    mt19937_64 rng;
    int root = 0;

    AffineSequenceTreap(unsigned long long seed = 712367821) : rng(seed) {}

    int size() const { return a[root].siz; }

    void pull(int p)
    {
        a[p].siz = a[a[p].l].siz + a[a[p].r].siz + 1;
        a[p].sum = a[a[p].l].sum + a[p].val + a[a[p].r].sum;
    }

    void apply(int p, Z b, Z c)
    {
        if (!p) return;
        a[p].val = b * a[p].val + c;
        a[p].sum = b * a[p].sum + c * Z(a[p].siz);
        a[p].mul = b * a[p].mul;
        a[p].add = b * a[p].add + c;
    }

    void flip(int p)
    {
        if (!p) return;
        swap(a[p].l, a[p].r);
        a[p].rev = !a[p].rev;
    }

    void push(int p)
    {
        if (a[p].rev)
        {
            flip(a[p].l);
            flip(a[p].r);
            a[p].rev = false;
        }
        if (a[p].mul.v != Z(1).v || a[p].add.v)
        {
            apply(a[p].l, a[p].mul, a[p].add);
            apply(a[p].r, a[p].mul, a[p].add);
            a[p].mul = 1;
            a[p].add = 0;
        }
    }

    // Split into the first k elements and the rest.
    void split(int p, int k, int &l, int &r)
    {
        if (!p)
        {
            l = r = 0;
            return;
        }
        push(p);
        int left = a[a[p].l].siz;
        if (k > left)
        {
            l = p;
            split(a[p].r, k - left - 1, a[p].r, r);
        }
        else
        {
            r = p;
            split(a[p].l, k, l, a[p].l);
        }
        pull(p);
    }

    int merge(int l, int r)
    {
        if (!l || !r) return l ? l : r;
        if (a[l].pri > a[r].pri)
        {
            push(l);
            a[l].r = merge(a[l].r, r);
            pull(l);
            return l;
        }
        push(r);
        a[r].l = merge(l, a[r].l);
        pull(r);
        return r;
    }

    // Insert after k elements; deleted nodes are not recycled.
    void insert(int k, Z value)
    {
        assert(0 <= k && k <= size());
        int p = a.size(), l, r;
        a.push_back({0, 0, 1, value, value, 1, 0, rng(), false});
        split(root, k, l, r);
        root = merge(merge(l, p), r);
    }

    // All range operations use nonempty 1-based inclusive intervals.
    void cut(int l, int r, int &x, int &y, int &z)
    {
        assert(1 <= l && l <= r && r <= size());
        split(root, r, y, z);
        split(y, l - 1, x, y);
    }

    void erase(int l, int r)
    {
        int x, y, z;
        cut(l, r, x, y, z);
        root = merge(x, z);
    }

    void reverse(int l, int r)
    {
        int x, y, z;
        cut(l, r, x, y, z);
        flip(y);
        root = merge(merge(x, y), z);
    }

    void affine(int l, int r, Z b, Z c)
    {
        int x, y, z;
        cut(l, r, x, y, z);
        apply(y, b, c);
        root = merge(merge(x, y), z);
    }

    Z query(int l, int r)
    {
        int x, y, z;
        cut(l, r, x, y, z);
        Z ans = a[y].sum;
        root = merge(merge(x, y), z);
        return ans;
    }

    void collect(int p, vector<Z> &out)
    {
        if (!p) return;
        push(p);
        collect(a[p].l, out);
        out.push_back(a[p].val);
        collect(a[p].r, out);
    }

    vector<Z> values()
    {
        vector<Z> out;
        collect(root, out);
        return out;
    }
};
