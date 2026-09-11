#pragma once
#include <algorithm>
#include <cassert>
#include <numeric>
#include <vector>
#include <utility>
using namespace std;

// Declare large instances globally or static. N is the largest legal vertex ID.
template<int N> struct Disjoint_Set
{
    int n, fa[N + 1], siz[N + 1];
    void Init ( int size )
    {
        assert(size <= N);
        n = size;
        iota(fa, fa + n + 1, 0);
        fill(siz, siz + n + 1, 1);
    }
    int Find ( int x )
    {
        int root = x;
        while ( root != fa[root] )
            root = fa[root];
        while ( x != root )
        {
            int next = fa[x];
            fa[x] = root;
            x = next;
        }
        return root;
    }
    bool Merge ( int x, int y )
    {
        x = Find(x); y = Find(y);
        if ( x == y ) return false;
        if ( siz[x] < siz[y] ) swap(x, y);
        fa[y] = x; siz[x] += siz[y];
        return true;
    }
};

template<int N, class T = long long> struct Binary_Indexed_Tree
{
    int n;
    T tree[N + 1];
    void Init ( int size )
    {
        assert(size <= N); n = size;
        fill(tree, tree + n + 1, T(0));
    }
    void Insert ( int x, T value )
    {
        assert(x >= 1);
        for ( ; x <= n; x += x & -x ) tree[x] += value;
    }
    T Sum ( int x ) const
    {
        T answer = 0;
        for ( ; x; x -= x & -x ) answer += tree[x];
        return answer;
    }
    T Query ( int L, int R ) const { return Sum(R) - Sum(L - 1); }
    int Kth ( T k ) const
    {
        assert(k > 0); int now = 0, step = 1;
        while ( step <= n / 2 ) step <<= 1;
        for ( ; step; step >>= 1 )
            if ( now + step <= n && tree[now + step] < k )
            {
                now += step; k -= tree[now];
            }
        return now + 1;
    }
};

template<int N> struct Segment_Tree
{
    int n;
    long long tree[4 * N + 5], tag[4 * N + 5];
    void Init ( int size )
    {
        assert(size > 0 && size <= N); n = size;
        fill(tree, tree + 4 * n + 5, 0);
        fill(tag, tag + 4 * n + 5, 0);
    }
    void Update ( int now, int L, int R, long long value )
    {
        tree[now] += (R - L + 1) * value;
        tag[now] += value;
    }
    void Push_Up ( int now ) { tree[now] = tree[now << 1] + tree[now << 1 | 1]; }
    void Push_Down ( int now, int L, int R )
    {
        int mid = (L + R) >> 1;
        Update(now << 1, L, mid, tag[now]);
        Update(now << 1 | 1, mid + 1, R, tag[now]);
        tag[now] = 0;
    }
    void Insert ( int ql, int qr, long long value ) { Insert(1, 1, n, ql, qr, value); }
    void Insert ( int now, int L, int R, int ql, int qr, long long value )
    {
        if ( ql <= L && R <= qr ) return Update(now, L, R, value);
        Push_Down(now, L, R);
        int mid = (L + R) >> 1;
        if ( ql <= mid ) Insert(now << 1, L, mid, ql, qr, value);
        if ( qr > mid ) Insert(now << 1 | 1, mid + 1, R, ql, qr, value);
        Push_Up(now);
    }
    long long Query ( int ql, int qr ) { return Query(1, 1, n, ql, qr); }
    long long Query ( int now, int L, int R, int ql, int qr )
    {
        if ( ql <= L && R <= qr ) return tree[now];
        Push_Down(now, L, R);
        int mid = (L + R) >> 1;
        long long answer = 0;
        if ( ql <= mid ) answer += Query(now << 1, L, mid, ql, qr);
        if ( qr > mid ) answer += Query(now << 1 | 1, mid + 1, R, ql, qr);
        return answer;
    }
};

template<int N> struct Rollback_DSU
{
    int fa[N + 1], siz[N + 1];
    vector<pair<int,int>> history;
    void Init ( int n )
    {
        assert(n <= N); history.clear();
        iota(fa, fa + n + 1, 0); fill(siz, siz + n + 1, 1);
    }
    int Find ( int x ) const
    {
        while ( fa[x] != x ) x = fa[x];
        return x;
    }
    int Snapshot () const { return (int)history.size(); }
    bool Merge ( int x, int y )
    {
        x = Find(x); y = Find(y);
        if ( x == y ) return false;
        if ( siz[x] < siz[y] ) swap(x, y);
        history.push_back({y, siz[x]});
        fa[y] = x; siz[x] += siz[y];
        return true;
    }
    void Rollback ( int time )
    {
        assert(0 <= time && time <= Snapshot());
        while ( Snapshot() > time )
        {
            auto [y, size] = history.back(); history.pop_back();
            siz[fa[y]] = size; fa[y] = y;
        }
    }
};

struct Xor_Basis
{
    unsigned long long base[64]{};
    bool Insert ( unsigned long long x )
    {
        for ( int i = 63; i >= 0; i -- )
        {
            if ( !(x >> i & 1) ) continue;
            if ( !base[i] ) { base[i] = x; return true; }
            x ^= base[i];
        }
        return false;
    }
    unsigned long long Query ( unsigned long long x = 0 ) const
    {
        for ( int i = 63; i >= 0; i -- ) x = max(x, x ^ base[i]);
        return x;
    }
};
