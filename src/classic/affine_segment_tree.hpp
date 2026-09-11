#pragma once
#include <cassert>
#include <vector>
using namespace std;

template <int N> struct Affine_Segment_Tree
{
    using ll = long long;

    struct Node
    {
        ll sum = 0, mul = 1, add = 0;
    };

    int n, mod;
    Node t[4 * N + 4];

    void Init(const vector<ll> &a, int modulus)
    {
        n = a.size();
        mod = modulus;
        assert(0 < n && n <= N && mod > 0);
        Build(1, 1, n, a);
    }

    ll Norm(ll x) const
    {
        x %= mod;
        if ( x < 0 )
            x += mod;
        return x;
    }

    void Push_Up(int p)
    {
        t[p].sum = (t[p * 2].sum + t[p * 2 + 1].sum) % mod;
    }

    void Build(int p, int l, int r, const vector<ll> &a)
    {
        t[p] = Node{};
        if ( l == r )
        {
            t[p].sum = Norm(a[l - 1]);
            return;
        }
        int m = (l + r) / 2;
        Build(p * 2, l, m, a);
        Build(p * 2 + 1, m + 1, r, a);
        Push_Up(p);
    }

    // New transform follows the old pending transform: x -> x*a+b.
    void Apply(int p, int len, ll a, ll b)
    {
        t[p].sum = (t[p].sum * a % mod + len * b % mod) % mod;
        t[p].mul = t[p].mul * a % mod;
        t[p].add = (t[p].add * a % mod + b) % mod;
    }

    void Push_Down(int p, int l, int r)
    {
        if ( t[p].mul == 1 && t[p].add == 0 )
            return;
        int m = (l + r) / 2;
        Apply(p * 2, m - l + 1, t[p].mul, t[p].add);
        Apply(p * 2 + 1, r - m, t[p].mul, t[p].add);
        t[p].mul = 1;
        t[p].add = 0;
    }

    void Update(int l, int r, ll a, ll b)
    {
        assert(1 <= l && l <= r && r <= n);
        Update(1, 1, n, l, r, Norm(a), Norm(b));
    }

    void Update(int p, int l, int r, int ql, int qr, ll a, ll b)
    {
        if ( ql <= l && r <= qr )
        {
            Apply(p, r - l + 1, a, b);
            return;
        }
        Push_Down(p, l, r);
        int m = (l + r) / 2;
        if ( ql <= m )
            Update(p * 2, l, m, ql, qr, a, b);
        if ( qr > m )
            Update(p * 2 + 1, m + 1, r, ql, qr, a, b);
        Push_Up(p);
    }

    ll Query(int l, int r)
    {
        assert(1 <= l && l <= r && r <= n);
        return Query(1, 1, n, l, r);
    }

    ll Query(int p, int l, int r, int ql, int qr)
    {
        if ( ql <= l && r <= qr )
            return t[p].sum;
        Push_Down(p, l, r);
        int m = (l + r) / 2;
        ll answer = 0;
        if ( ql <= m )
            answer += Query(p * 2, l, m, ql, qr);
        if ( qr > m )
            answer += Query(p * 2 + 1, m + 1, r, ql, qr);
        return answer % mod;
    }
};
