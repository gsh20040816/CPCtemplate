#pragma once
#include <cassert>
#include <numeric>
#include <optional>
#include <random>
#include <utility>
#include <vector>
using namespace std;

template <int N> struct Gcd_Sequence_Treap
{
    using U = unsigned long long;

    struct Node
    {
        int l = 0, r = 0, siz = 0, tag = 0;
        int cnt[2]{};
        U val = 0, g[2]{}, pri = 0;
    };

    Node tree[N + 1];
    int tot = 0;
    vector<int> recycled;
    mt19937_64 rng;
    int root = 0;

    void Init(U seed = 712367821)
    {
        root = 0;
        tot = 0;
        tree[0] = Node{};
        recycled.clear();
        rng.seed(seed);
    }

    int Size() const
    {
        return tree[root].siz;
    }

    int New_Node(U value, int tag)
    {
        assert(tag == 0 || tag == 1);
        int p;
        if ( recycled.empty() )
        {
            assert(tot < N);
            p = ++tot;
            tree[p] = Node{};
        }
        else
        {
            p = recycled.back();
            recycled.pop_back();
            tree[p] = Node{};
        }
        tree[p].siz = 1;
        tree[p].val = value;
        tree[p].tag = tag;
        tree[p].cnt[tag] = 1;
        tree[p].g[tag] = value;
        tree[p].pri = rng();
        return p;
    }

    void Push_Up(int p)
    {
        int l = tree[p].l, r = tree[p].r;
        tree[p].siz = tree[l].siz + tree[r].siz + 1;
        for ( int t = 0; t < 2; t++ )
        {
            tree[p].cnt[t] = tree[l].cnt[t] + tree[r].cnt[t] + (tree[p].tag == t);
            tree[p].g[t] = gcd(tree[l].g[t], tree[r].g[t]);
            if ( tree[p].tag == t )
                tree[p].g[t] = gcd(tree[p].g[t], tree[p].val);
        }
    }

    void Split(int p, int k, int &l, int &r)
    {
        if ( !p )
        {
            l = 0;
            r = 0;
            return;
        }
        int left = tree[tree[p].l].siz;
        if ( k > left )
        {
            l = p;
            Split(tree[p].r, k - left - 1, tree[p].r, r);
        }
        else
        {
            r = p;
            Split(tree[p].l, k, l, tree[p].l);
        }
        Push_Up(p);
    }

    int Merge(int l, int r)
    {
        if ( !l || !r )
            return l ? l : r;
        if ( tree[l].pri > tree[r].pri )
        {
            tree[l].r = Merge(tree[l].r, r);
            Push_Up(l);
            return l;
        }
        tree[r].l = Merge(l, tree[r].l);
        Push_Up(r);
        return r;
    }

    void Rebuild(int p)
    {
        if ( !p )
            return;
        Rebuild(tree[p].l);
        Rebuild(tree[p].r);
        Push_Up(p);
    }

    void Release(int p)
    {
        if ( !p )
            return;
        Release(tree[p].l);
        Release(tree[p].r);
        recycled.push_back(p);
    }

    // O(n) GCD calls; replaces the current sequence.
    void Build(const vector<pair<U, int>> &v)
    {
        assert(v.size() <= N);
        tot = 0;
        tree[0] = Node{};
        recycled.clear();
        root = 0;
        vector<int> st;
        for ( auto [value, tag] : v )
        {
            int p = New_Node(value, tag), last = 0;
            while ( !st.empty() && tree[st.back()].pri < tree[p].pri )
            {
                last = st.back();
                st.pop_back();
            }
            tree[p].l = last;
            if ( !st.empty() )
                tree[st.back()].r = p;
            st.push_back(p);
        }
        if ( st.empty() )
            return;
        root = st.front();
        Rebuild(root);
    }

    // Insert after the first k entries. Range operations below are 1-based.
    void Insert(int k, U value, int tag)
    {
        assert(0 <= k && k <= Size());
        int p = New_Node(value, tag), l, r;
        Split(root, k, l, r);
        root = Merge(Merge(l, p), r);
    }

    void Erase(int l, int r)
    {
        assert(1 <= l && l <= r && r <= Size());
        int x, y, z;
        Split(root, r, y, z);
        Split(y, l - 1, x, y);
        root = Merge(x, z);
        Release(y);
    }

    void Set(int k, U value)
    {
        assert(1 <= k && k <= Size());
        int x, y, z;
        Split(root, k, y, z);
        Split(y, k - 1, x, y);
        tree[y].val = value;
        Push_Up(y);
        root = Merge(Merge(x, y), z);
    }

    void Toggle(int k)
    {
        assert(1 <= k && k <= Size());
        int x, y, z;
        Split(root, k, y, z);
        Split(y, k - 1, x, y);
        tree[y].tag ^= 1;
        Push_Up(y);
        root = Merge(Merge(x, y), z);
    }

    optional<U> Query(int l, int r, int tag)
    {
        assert(1 <= l && l <= r && r <= Size());
        assert(tag == 0 || tag == 1);
        int x, y, z;
        Split(root, r, y, z);
        Split(y, l - 1, x, y);
        optional<U> answer;
        if ( tree[y].cnt[tag] )
            answer = tree[y].g[tag];
        root = Merge(Merge(x, y), z);
        return answer;
    }
};
