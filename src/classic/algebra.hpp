#pragma once
#include "number_theory.hpp"

template <int mod> struct Linear_Algebra
{
    using Z = Mod_Int<mod>;
    using Matrix = vector<vector<Z>>;

    struct Solution
    {
        bool consistent;
        int rank;
        vector<Z> particular;
        Matrix kernel;
    };

    // Augmented m x (n+1), prime modulus. Empty system needs explicit n.
    static Solution Solve(Matrix a, int n)
    {
        int m = (int)a.size(), row = 0;
        vector<int> where(n, -1);
        for ( const auto &v : a )
            assert((int)v.size() == n + 1);
        for ( int col = 0; col < n && row < m; col++ )
        {
            int p = row;
            while ( p < m && !a[p][col].v )
                ++p;
            if ( p == m )
                continue;
            swap(a[p], a[row]);
            Z Inv = a[row][col].Inv();
            for ( int j = col; j <= n; j++ )
                a[row][j] = a[row][j] * Inv;
            for ( int i = 0; i < m; i++ )
                if ( i != row && a[i][col].v )
                {
                    Z f = a[i][col];
                    for ( int j = col; j <= n; j++ )
                        a[i][j] = a[i][j] - f * a[row][j];
                }
            where[col] = row++;
        }
        for ( int i = row; i < m; i++ )
            if ( a[i][n].v )
                return {false, row, {}, {}};
        Solution ans{true, row, vector<Z>(n), {}};
        for ( int j = 0; j < n; j++ )
            if ( where[j] != -1 )
                ans.particular[j] = a[where[j]][n];
        for ( int j = 0; j < n; j++ )
            if ( where[j] == -1 )
            {
                vector<Z> v(n);
                v[j] = 1;
                for ( int k = 0; k < n; k++ )
                    if ( where[k] != -1 )
                        v[k] = Z(0) - a[where[k]][j];
                ans.kernel.push_back(v);
            }
        return ans;
    }

    static Z Determinant(Matrix a)
    {
        int n = (int)a.size();
        Z ans = 1;
        for ( int i = 0; i < n; i++ )
        {
            assert((int)a[i].size() == n);
            int p = i;
            while ( p < n && !a[p][i].v )
                ++p;
            if ( p == n )
                return 0;
            if ( p != i )
            {
                swap(a[p], a[i]);
                ans = Z(0) - ans;
            }
            ans = ans * a[i][i];
            Z Inv = a[i][i].Inv();
            for ( int j = i + 1; j < n; j++ )
            {
                Z f = a[j][i] * Inv;
                for ( int k = i; k < n; k++ )
                    a[j][k] = a[j][k] - f * a[i][k];
            }
        }
        return ans;
    }

    static Matrix Multiply(const Matrix &a, const Matrix &b)
    {
        assert(!a.empty() && !b.empty());
        int n = a.size(), m = b[0].size(), k = b.size();
        assert((int)a[0].size() == k);
        Matrix c(n, vector<Z>(m));
        for ( int i = 0; i < n; i++ )
            for ( int t = 0; t < k; t++ )
                for ( int j = 0; j < m; j++ )
                    c[i][j] = c[i][j] + a[i][t] * b[t][j];
        return c;
    }

    static Matrix Power(Matrix a, unsigned long long e)
    {
        int n = a.size();
        assert(n > 0 && (int)a[0].size() == n);
        Matrix r(n, vector<Z>(n));
        for ( int i = 0; i < n; i++ )
            r[i][i] = 1;
        for ( ; e; e >>= 1, a = Multiply(a, a) )
            if ( e & 1 )
                r = Multiply(r, a);
        return r;
    }

    // Undirected multigraph, vertices 0..n-1; loops ignored.
    static Z Spanning_Trees(int n, const vector<pair<int, int>> &edges)
    {
        assert(n > 0);
        Matrix lap(n, vector<Z>(n));
        for ( auto [u, v] : edges )
            if ( u != v )
            {
                lap[u][u] = lap[u][u] + 1;
                lap[v][v] = lap[v][v] + 1;
                lap[u][v] = lap[u][v] - 1;
                lap[v][u] = lap[v][u] - 1;
            }
        lap.pop_back();
        for ( auto &row : lap )
            row.pop_back();
        return Determinant(lap);
    }
};

struct Du_Jiao
{
    using ll = long long;
    using I = __int128_t;
    int limit;
    vector<ll> pmu, pphi;
    unordered_map<ll, ll> mmu;
    unordered_map<ll, I> mphi;

    Du_Jiao(int limit) : limit(limit), pmu(limit + 1), pphi(limit + 1)
    {
        assert(limit >= 1);
        Linear_Sieve s(limit);
        for ( int i = 1; i <= limit; i++ )
        {
            pmu[i] = pmu[i - 1] + s.mu[i];
            pphi[i] = pphi[i - 1] + s.phi[i];
        }
    }

    ll Mertens(ll n)
    {
        if ( n <= limit )
            return pmu[n];
        if ( mmu.count(n) )
            return mmu[n];
        ll ans = 1;
        for ( ll l = 2, r; l <= n; l = r + 1 )
        {
            r = n / (n / l);
            ans -= (r - l + 1) * Mertens(n / l);
        }
        return mmu[n] = ans;
    }

    I Totient_Sum(ll n)
    {
        if ( n <= limit )
            return pphi[n];
        if ( mphi.count(n) )
            return mphi[n];
        I ans = I(n) * (n + 1) / 2;
        for ( ll l = 2, r; l <= n; l = r + 1 )
        {
            r = n / (n / l);
            ans -= I(r - l + 1) * Totient_Sum(n / l);
        }
        return mphi[n] = ans;
    }
};

struct Discrete_Log
{
    using ll = long long;

    // 1<=m<=1e12; Expected O(sqrt(m)) time, O(sqrt(m)) storage. Smallest x>=0, or -1.
    static ll Solve(ll a, ll b, ll m)
    {
        assert(m >= 1 && m <= 1000000000000LL);
        a = (a % m + m) % m;
        b = (b % m + m) % m;
        if ( m == 1 || b == 1 )
            return 0;
        if ( a == 1 )
            return -1;
        ll offset = 0, k = 1;
        for ( ll g; (g = gcd(a, m)) > 1; )
        {
            if ( b == k )
                return offset;
            if ( b % g )
                return -1;
            b /= g;
            m /= g;
            k = (__int128)k * (a / g) % m;
            ++offset;
        }
        ll target = (__int128)b * Number_Theory::Inverse(k, m) % m;
        ll step = sqrtl(m) + 1;
        unordered_map<ll, ll> baby;
        baby.reserve(step);
        ll cur = 1 % m;
        for ( ll j = 0; j < step; j++ )
        {
            if ( !baby.count(cur) )
                baby[cur] = j;
            cur = (__int128)cur * a % m;
        }
        ll Inv = Number_Theory::Inverse(Number_Theory::Power(a, step, m), m);
        cur = target;
        for ( ll i = 0; i <= step; i++ )
        {
            auto it = baby.find(cur);
            if ( it != baby.end() )
                return offset + i * step + it->second;
            cur = (__int128)cur * Inv % m;
        }
        return -1;
    }
};
