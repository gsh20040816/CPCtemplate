#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct NumberTheory
{
    using ll = long long;
    using ull = unsigned long long;
    using i128 = __int128_t;
    using u128 = __uint128_t;

    static ull mul(ull a, ull b, ull m)
    {
        return u128(a) * b % m;
    }

    static ull power(ull a, ull b, ull m)
    {
        assert(m);
        ull r = 1 % m;
        a %= m;
        for (; b; b >>= 1, a = mul(a, a, m))
            if (b & 1)
                r = mul(r, a, m);
        return r;
    }

    static bool prime(ull n)
    {
        if (n < 2)
            return false;
        for (ull p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37})
            if (n % p == 0)
                return n == p;
        ull d = n - 1;
        int s = 0;
        while (!(d & 1))
        {
            d >>= 1;
            ++s;
        }
        for (ull a :
             {2ULL, 325ULL, 9375ULL, 28178ULL, 450775ULL, 9780504ULL, 1795265022ULL})
        {
            if (a % n == 0)
                continue;
            ull x = power(a, d, n);
            if (x == 1 || x == n - 1)
                continue;
            bool ok = false;
            for (int j = 1; j < s; j++)
            {
                x = mul(x, x, n);
                if (x == n - 1)
                {
                    ok = true;
                    break;
                }
            }
            if (!ok)
                return false;
        }
        return true;
    }

    static i128 exgcd(i128 a, i128 b, i128 &x, i128 &y)
    {
        if (!b)
        {
            x = 1;
            y = 0;
            return a;
        }
        i128 d = exgcd(b, a % b, y, x);
        y -= a / b * x;
        return d;
    }

    static ll inverse(ll a, ll m)
    {
        assert(m > 0);
        a %= m;
        if (a < 0)
            a += m;
        i128 x, y;
        if (exgcd(a, m, x, y) != 1)
            return -1;
        return (x % m + m) % m;
    }

    // x = r (mod m); false means inconsistent. Throws if lcm exceeds int64.
    static bool crt(ll &r, ll &m, ll b, ll n)
    {
        assert(m > 0 && n > 0);
        r %= m;
        if (r < 0)
            r += m;
        b %= n;
        if (b < 0)
            b += n;
        i128 x, y;
        ll g = (ll)exgcd(m, n, x, y);
        i128 diff = i128(b) - r;
        if (diff % g)
            return false;
        i128 q = n / g, k = (diff / g * x % q + q) % q, mod = i128(m) * q;
        if (mod > LLONG_MAX)
            throw overflow_error("CRT modulus");
        r = (r + i128(m) * k) % mod;
        m = (ll)mod;
        return true;
    }

    // sum_{i=0}^{n-1} floor((a*i+b)/m), signed a,b; 0<=n<=1e9, 1<=m<=1e9.
    static i128 floor_sum(ll n, ll m, ll a, ll b)
    {
        assert(n >= 0 && m > 0);
        i128 ans = 0;
        auto norm = [&](ll &v)
        {
            ll q = v / m;
            if (v % m < 0)
                --q;
            v = (ll)(i128(v) - i128(q) * m);
            return q;
        };
        ans += i128(norm(a)) * n * (n - 1) / 2;
        ans += i128(norm(b)) * n;
        while (true)
        {
            ans += i128(n) * (n - 1) / 2 * (a / m);
            a %= m;
            ans += i128(n) * (b / m);
            b %= m;
            i128 y = i128(a) * n + b;
            if (y < m)
                break;
            n = (ll)(y / m);
            b = (ll)(y % m);
            swap(a, m);
        }
        return ans;
    }
};

struct PollardRho
{
    using ull = unsigned long long;
    using u128 = __uint128_t;
    mt19937_64 rng;

    PollardRho(ull seed = 712367821) : rng(seed)
    {
    }

    ull rho(ull n)
    {
        if (n % 2 == 0)
            return 2;
        for (;;)
        {
            ull c = rng() % (n - 1) + 1, x = rng() % n, y = x, d = 1;
            auto f = [&](ull v)
            {
                return (NumberTheory::mul(v, v, n) + u128(c)) % n;
            };
            // Retry bounded attempts; Las Vegas: only exact divisors returned.
            for (int i = 0; i < 200000 && d == 1; i++)
            {
                x = f(x);
                y = f(f(y));
                d = gcd(x > y ? x - y : y - x, n);
            }
            if (1 < d && d < n)
                return d;
        }
    }

    void split(ull n, vector<ull> &a)
    {
        if (n == 1)
            return;
        if (NumberTheory::prime(n))
        {
            a.push_back(n);
            return;
        }
        ull d = rho(n);
        split(d, a);
        split(n / d, a);
    }

    vector<ull> factor(ull n)
    {
        assert(n >= 1);
        vector<ull> a;
        split(n, a);
        sort(a.begin(), a.end());
        return a;
    }
};

struct LinearSieve
{
    vector<int> prime, lp, phi, mu;

    LinearSieve(int n) : lp(n + 1), phi(n + 1), mu(n + 1)
    {
        if (n)
            phi[1] = mu[1] = 1;
        for (int i = 2; i <= n; i++)
        {
            if (!lp[i])
            {
                lp[i] = i;
                prime.push_back(i);
                phi[i] = i - 1;
                mu[i] = -1;
            }
            for (int p : prime)
            {
                if (p > n / i)
                    break;
                int j = i * p;
                lp[j] = p;
                if (i % p == 0)
                {
                    phi[j] = phi[i] * p;
                    mu[j] = 0;
                    break;
                }
                phi[j] = phi[i] * (p - 1);
                mu[j] = -mu[i];
            }
        }
    }
};

template <int mod> struct ModInt
{
    int v;

    ModInt(long long x = 0) : v((x % mod + mod) % mod)
    {
    }

    ModInt operator+(ModInt b) const
    {
        return ModInt((long long)v + b.v);
    }

    ModInt operator-(ModInt b) const
    {
        return ModInt((long long)v - b.v);
    }

    ModInt operator*(ModInt b) const
    {
        return ModInt(1LL * v * b.v);
    }

    ModInt pow(long long e) const
    {
        assert(e >= 0);
        ModInt a = *this, r = 1;
        for (; e; e >>= 1, a = a * a)
            if (e & 1)
                r = r * a;
        return r;
    }

    ModInt inv() const
    {
        assert(v);
        return pow(mod - 2);
    } // prime modulus

    ModInt operator/(ModInt b) const
    {
        return *this * b.inv();
    }
};

template <int mod> struct Binomial
{
    using Z = ModInt<mod>;
    vector<Z> fac, ifac;

    Binomial(int n) : fac(n + 1), ifac(n + 1)
    {
        assert(0 <= n && n < mod);
        fac[0] = 1;
        for (int i = 1; i <= n; i++)
            fac[i] = fac[i - 1] * i;
        ifac[n] = fac[n].inv();
        for (int i = n; i; i--)
            ifac[i - 1] = ifac[i] * i;
    }

    Z choose(int n, int k) const
    {
        if (k < 0 || k > n)
            return 0;
        assert(n < (int)fac.size());
        return fac[n] * ifac[k] * ifac[n - k];
    }
};


template <int mod> struct LinearAlgebra
{
    using Z = ModInt<mod>;
    using Matrix = vector<vector<Z>>;

    struct Solution
    {
        bool consistent;
        int rank;
        vector<Z> particular;
        Matrix kernel;
    };

    // Augmented m x (n+1), prime modulus. Empty system needs explicit n.
    static Solution solve(Matrix a, int n)
    {
        int m = (int)a.size(), row = 0;
        vector<int> where(n, -1);
        for (const auto &v : a)
            assert((int)v.size() == n + 1);
        for (int col = 0; col < n && row < m; col++)
        {
            int p = row;
            while (p < m && !a[p][col].v)
                ++p;
            if (p == m)
                continue;
            swap(a[p], a[row]);
            Z inv = a[row][col].inv();
            for (int j = col; j <= n; j++)
                a[row][j] = a[row][j] * inv;
            for (int i = 0; i < m; i++)
                if (i != row && a[i][col].v)
                {
                    Z f = a[i][col];
                    for (int j = col; j <= n; j++)
                        a[i][j] = a[i][j] - f * a[row][j];
                }
            where[col] = row++;
        }
        for (int i = row; i < m; i++)
            if (a[i][n].v)
                return {false, row, {}, {}};
        Solution ans{true, row, vector<Z>(n), {}};
        for (int j = 0; j < n; j++)
            if (where[j] != -1)
                ans.particular[j] = a[where[j]][n];
        for (int j = 0; j < n; j++)
            if (where[j] == -1)
            {
                vector<Z> v(n);
                v[j] = 1;
                for (int k = 0; k < n; k++)
                    if (where[k] != -1)
                        v[k] = Z(0) - a[where[k]][j];
                ans.kernel.push_back(v);
            }
        return ans;
    }

    static Z determinant(Matrix a)
    {
        int n = (int)a.size();
        Z ans = 1;
        for (int i = 0; i < n; i++)
        {
            assert((int)a[i].size() == n);
            int p = i;
            while (p < n && !a[p][i].v)
                ++p;
            if (p == n)
                return 0;
            if (p != i)
            {
                swap(a[p], a[i]);
                ans = Z(0) - ans;
            }
            ans = ans * a[i][i];
            Z inv = a[i][i].inv();
            for (int j = i + 1; j < n; j++)
            {
                Z f = a[j][i] * inv;
                for (int k = i; k < n; k++)
                    a[j][k] = a[j][k] - f * a[i][k];
            }
        }
        return ans;
    }

    static Matrix multiply(const Matrix &a, const Matrix &b)
    {
        assert(!a.empty() && !b.empty());
        int n = a.size(), m = b[0].size(), k = b.size();
        assert((int)a[0].size() == k);
        Matrix c(n, vector<Z>(m));
        for (int i = 0; i < n; i++)
            for (int t = 0; t < k; t++)
                for (int j = 0; j < m; j++)
                    c[i][j] = c[i][j] + a[i][t] * b[t][j];
        return c;
    }

    static Matrix power(Matrix a, unsigned long long e)
    {
        int n = a.size();
        assert(n > 0 && (int)a[0].size() == n);
        Matrix r(n, vector<Z>(n));
        for (int i = 0; i < n; i++)
            r[i][i] = 1;
        for (; e; e >>= 1, a = multiply(a, a))
            if (e & 1)
                r = multiply(r, a);
        return r;
    }

    // Undirected multigraph, vertices 0..n-1; loops ignored.
    static Z spanning_trees(int n, const vector<pair<int, int>> &edges)
    {
        assert(n > 0);
        Matrix lap(n, vector<Z>(n));
        for (auto [u, v] : edges)
            if (u != v)
            {
                lap[u][u] = lap[u][u] + 1;
                lap[v][v] = lap[v][v] + 1;
                lap[u][v] = lap[u][v] - 1;
                lap[v][u] = lap[v][u] - 1;
            }
        lap.pop_back();
        for (auto &row : lap)
            row.pop_back();
        return determinant(lap);
    }
};

struct DuJiao
{
    using ll = long long;
    using I = __int128_t;
    int limit;
    vector<ll> pmu, pphi;
    unordered_map<ll, ll> mmu;
    unordered_map<ll, I> mphi;

    DuJiao(int limit) : limit(limit), pmu(limit + 1), pphi(limit + 1)
    {
        assert(limit >= 1);
        LinearSieve s(limit);
        for (int i = 1; i <= limit; i++)
        {
            pmu[i] = pmu[i - 1] + s.mu[i];
            pphi[i] = pphi[i - 1] + s.phi[i];
        }
    }

    ll mertens(ll n)
    {
        if (n <= limit)
            return pmu[n];
        if (mmu.count(n))
            return mmu[n];
        ll ans = 1;
        for (ll l = 2, r; l <= n; l = r + 1)
        {
            r = n / (n / l);
            ans -= (r - l + 1) * mertens(n / l);
        }
        return mmu[n] = ans;
    }

    I totient_sum(ll n)
    {
        if (n <= limit)
            return pphi[n];
        if (mphi.count(n))
            return mphi[n];
        I ans = I(n) * (n + 1) / 2;
        for (ll l = 2, r; l <= n; l = r + 1)
        {
            r = n / (n / l);
            ans -= I(r - l + 1) * totient_sum(n / l);
        }
        return mphi[n] = ans;
    }
};

struct DiscreteLog
{
    using ll = long long;

    // 1<=m<=1e12; Expected O(sqrt(m)) time, O(sqrt(m)) storage. Smallest x>=0, or -1.
    static ll solve(ll a, ll b, ll m)
    {
        assert(m >= 1 && m <= 1000000000000LL);
        a = (a % m + m) % m;
        b = (b % m + m) % m;
        if (m == 1 || b == 1)
            return 0;
        if (a == 1)
            return -1;
        ll offset = 0, k = 1;
        for (ll g; (g = gcd(a, m)) > 1;)
        {
            if (b == k)
                return offset;
            if (b % g)
                return -1;
            b /= g;
            m /= g;
            k = (__int128)k * (a / g) % m;
            ++offset;
        }
        ll target = (__int128)b * NumberTheory::inverse(k, m) % m;
        ll step = sqrtl(m) + 1;
        unordered_map<ll, ll> baby;
        baby.reserve(step);
        ll cur = 1 % m;
        for (ll j = 0; j < step; j++)
        {
            if (!baby.count(cur))
                baby[cur] = j;
            cur = (__int128)cur * a % m;
        }
        ll inv = NumberTheory::inverse(NumberTheory::power(a, step, m), m);
        cur = target;
        for (ll i = 0; i <= step; i++)
        {
            auto it = baby.find(cur);
            if (it != baby.end())
                return offset + i * step + it->second;
            cur = (__int128)cur * inv % m;
        }
        return -1;
    }
};

#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    long long a, p, b;
    while (std::cin >> a >> p >> b)
    {
        if (a == 0 && p == 0 && b == 0)
            break;
        long long answer = DiscreteLog::solve(a, b, p);
        if (answer == -1)
            std::cout << "No Solution\n";
        else
            std::cout << answer << '\n';
    }
}
