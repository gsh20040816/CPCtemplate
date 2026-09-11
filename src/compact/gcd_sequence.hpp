#pragma once
#include <cassert>
#include <numeric>
#include <optional>
#include <random>
#include <utility>
#include <vector>
using namespace std;

struct GcdSequenceTreap
{
    using U = unsigned long long;

    struct Node
    {
        int l = 0, r = 0, siz = 0, tag = 0;
        int cnt[2]{};
        U val = 0, g[2]{}, pri = 0;
    };

    vector<Node> a{Node{}};
    vector<int> recycled;
    mt19937_64 rng;
    int root = 0;

    GcdSequenceTreap(U seed = 712367821) : rng(seed)
    {
    }

    int size() const
    {
        return a[root].siz;
    }

    int node(U value, int tag)
    {
        assert(tag == 0 || tag == 1);
        int p;
        if (recycled.empty())
        {
            p = a.size();
            a.push_back(Node{});
        }
        else
        {
            p = recycled.back();
            recycled.pop_back();
            a[p] = Node{};
        }
        a[p].siz = 1;
        a[p].val = value;
        a[p].tag = tag;
        a[p].cnt[tag] = 1;
        a[p].g[tag] = value;
        a[p].pri = rng();
        return p;
    }

    void pull(int p)
    {
        int l = a[p].l, r = a[p].r;
        a[p].siz = a[l].siz + a[r].siz + 1;
        for (int t = 0; t < 2; t++)
        {
            a[p].cnt[t] = a[l].cnt[t] + a[r].cnt[t] + (a[p].tag == t);
            a[p].g[t] = gcd(a[l].g[t], a[r].g[t]);
            if (a[p].tag == t)
                a[p].g[t] = gcd(a[p].g[t], a[p].val);
        }
    }

    void split(int p, int k, int &l, int &r)
    {
        if (!p)
        {
            l = 0;
            r = 0;
            return;
        }
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
        if (!l || !r)
            return l ? l : r;
        if (a[l].pri > a[r].pri)
        {
            a[l].r = merge(a[l].r, r);
            pull(l);
            return l;
        }
        a[r].l = merge(l, a[r].l);
        pull(r);
        return r;
    }

    void rebuild(int p)
    {
        if (!p)
            return;
        rebuild(a[p].l);
        rebuild(a[p].r);
        pull(p);
    }

    void release(int p)
    {
        if (!p)
            return;
        release(a[p].l);
        release(a[p].r);
        recycled.push_back(p);
    }

    // O(n) GCD calls; replaces the current sequence.
    void build(const vector<pair<U, int>> &v)
    {
        a.assign(1, Node{});
        recycled.clear();
        root = 0;
        vector<int> st;
        for (auto [value, tag] : v)
        {
            int p = node(value, tag), last = 0;
            while (!st.empty() && a[st.back()].pri < a[p].pri)
            {
                last = st.back();
                st.pop_back();
            }
            a[p].l = last;
            if (!st.empty())
                a[st.back()].r = p;
            st.push_back(p);
        }
        if (st.empty())
            return;
        root = st.front();
        rebuild(root);
    }

    // Insert after the first k entries. Range operations below are 1-based.
    void insert(int k, U value, int tag)
    {
        assert(0 <= k && k <= size());
        int p = node(value, tag), l, r;
        split(root, k, l, r);
        root = merge(merge(l, p), r);
    }

    void erase(int l, int r)
    {
        assert(1 <= l && l <= r && r <= size());
        int x, y, z;
        split(root, r, y, z);
        split(y, l - 1, x, y);
        root = merge(x, z);
        release(y);
    }

    void set(int k, U value)
    {
        assert(1 <= k && k <= size());
        int x, y, z;
        split(root, k, y, z);
        split(y, k - 1, x, y);
        a[y].val = value;
        pull(y);
        root = merge(merge(x, y), z);
    }

    void toggle(int k)
    {
        assert(1 <= k && k <= size());
        int x, y, z;
        split(root, k, y, z);
        split(y, k - 1, x, y);
        a[y].tag ^= 1;
        pull(y);
        root = merge(merge(x, y), z);
    }

    optional<U> query(int l, int r, int tag)
    {
        assert(1 <= l && l <= r && r <= size());
        assert(tag == 0 || tag == 1);
        int x, y, z;
        split(root, r, y, z);
        split(y, l - 1, x, y);
        optional<U> answer;
        if (a[y].cnt[tag])
            answer = a[y].g[tag];
        root = merge(merge(x, y), z);
        return answer;
    }
};
