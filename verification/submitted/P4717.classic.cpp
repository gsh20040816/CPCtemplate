#include <algorithm>
#include <array>
#include <cassert>
#include <climits>
#include <cmath>
#include <functional>
#include <map>
#include <numeric>
#include <optional>
#include <queue>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;

struct Number_Theory
{
    using ll = long long;
    using ull = unsigned long long;
    using i128 = __int128_t;
    using u128 = __uint128_t;

    static ull Mul(ull a, ull b, ull m)
    {
        return u128(a) * b % m;
    }

    static ull Power(ull a, ull b, ull m)
    {
        assert(m);
        ull r = 1 % m;
        a %= m;
        for ( ; b; b >>= 1, a = Mul(a, a, m) )
            if ( b & 1 )
                r = Mul(r, a, m);
        return r;
    }

    static bool Prime(ull n)
    {
        if ( n < 2 )
            return false;
        for ( ull p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37} )
            if ( n % p == 0 )
                return n == p;
        ull d = n - 1;
        int s = 0;
        while ( !(d & 1) )
        {
            d >>= 1;
            ++s;
        }
        for ( ull a :
              {2ULL, 325ULL, 9375ULL, 28178ULL, 450775ULL, 9780504ULL, 1795265022ULL} )
        {
            if ( a % n == 0 )
                continue;
            ull x = Power(a, d, n);
            if ( x == 1 || x == n - 1 )
                continue;
            bool ok = false;
            for ( int j = 1; j < s; j++ )
            {
                x = Mul(x, x, n);
                if ( x == n - 1 )
                {
                    ok = true;
                    break;
                }
            }
            if ( !ok )
                return false;
        }
        return true;
    }

    static i128 Exgcd(i128 a, i128 b, i128 &x, i128 &y)
    {
        if ( !b )
        {
            x = 1;
            y = 0;
            return a;
        }
        i128 d = Exgcd(b, a % b, y, x);
        y -= a / b * x;
        return d;
    }

    static ll Inverse(ll a, ll m)
    {
        assert(m > 0);
        a %= m;
        if ( a < 0 )
            a += m;
        i128 x, y;
        if ( Exgcd(a, m, x, y) != 1 )
            return -1;
        return (x % m + m) % m;
    }

    // x = r (mod m); false means inconsistent. Throws if lcm exceeds int64.
    static bool Crt(ll &r, ll &m, ll b, ll n)
    {
        assert(m > 0 && n > 0);
        r %= m;
        if ( r < 0 )
            r += m;
        b %= n;
        if ( b < 0 )
            b += n;
        i128 x, y;
        ll g = (ll)Exgcd(m, n, x, y);
        i128 diff = i128(b) - r;
        if ( diff % g )
            return false;
        i128 q = n / g, k = (diff / g * x % q + q) % q, mod = i128(m) * q;
        if ( mod > LLONG_MAX )
            throw overflow_error("CRT modulus");
        r = (r + i128(m) * k) % mod;
        m = (ll)mod;
        return true;
    }

    // sum_{i=0}^{n-1} floor((a*i+b)/m), signed a,b; 0<=n<=1e9, 1<=m<=1e9.
    static i128 Floor_Sum(ll n, ll m, ll a, ll b)
    {
        assert(n >= 0 && m > 0);
        i128 ans = 0;
        auto norm = [&](ll &v)
        {
            ll q = v / m;
            if ( v % m < 0 )
                --q;
            v = (ll)(i128(v) - i128(q) * m);
            return q;
        };
        ans += i128(norm(a)) * n * (n - 1) / 2;
        ans += i128(norm(b)) * n;
        while ( true )
        {
            ans += i128(n) * (n - 1) / 2 * (a / m);
            a %= m;
            ans += i128(n) * (b / m);
            b %= m;
            i128 y = i128(a) * n + b;
            if ( y < m )
                break;
            n = (ll)(y / m);
            b = (ll)(y % m);
            swap(a, m);
        }
        return ans;
    }
};

struct Pollard_Rho
{
    using ull = unsigned long long;
    using u128 = __uint128_t;
    mt19937_64 rng;

    Pollard_Rho(ull seed = 712367821) : rng(seed)
    {
    }

    ull Rho(ull n)
    {
        if ( n % 2 == 0 )
            return 2;
        for ( ;; )
        {
            ull c = rng() % (n - 1) + 1, x = rng() % n, y = x, d = 1;
            auto f = [&](ull v)
            {
                return (Number_Theory::Mul(v, v, n) + u128(c)) % n;
            };
            // Retry bounded attempts; Las Vegas: only exact divisors returned.
            for ( int i = 0; i < 200000 && d == 1; i++ )
            {
                x = f(x);
                y = f(f(y));
                d = gcd(x > y ? x - y : y - x, n);
            }
            if ( 1 < d && d < n )
                return d;
        }
    }

    void Split(ull n, vector<ull> &a)
    {
        if ( n == 1 )
            return;
        if ( Number_Theory::Prime(n) )
        {
            a.push_back(n);
            return;
        }
        ull d = Rho(n);
        Split(d, a);
        Split(n / d, a);
    }

    vector<ull> Factor(ull n)
    {
        assert(n >= 1);
        vector<ull> a;
        Split(n, a);
        sort(a.begin(), a.end());
        return a;
    }
};

struct Linear_Sieve
{
    vector<int> Prime, lp, phi, mu;

    Linear_Sieve(int n) : lp(n + 1), phi(n + 1), mu(n + 1)
    {
        if ( n )
            phi[1] = mu[1] = 1;
        for ( int i = 2; i <= n; i++ )
        {
            if ( !lp[i] )
            {
                lp[i] = i;
                Prime.push_back(i);
                phi[i] = i - 1;
                mu[i] = -1;
            }
            for ( int p : Prime )
            {
                if ( p > n / i )
                    break;
                int j = i * p;
                lp[j] = p;
                if ( i % p == 0 )
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

template <int mod> struct Mod_Int
{
    int v;

    Mod_Int(long long x = 0) : v((x % mod + mod) % mod)
    {
    }

    Mod_Int operator+(Mod_Int b) const
    {
        return Mod_Int((long long)v + b.v);
    }

    Mod_Int operator-(Mod_Int b) const
    {
        return Mod_Int((long long)v - b.v);
    }

    Mod_Int operator*(Mod_Int b) const
    {
        return Mod_Int(1LL * v * b.v);
    }

    Mod_Int Pow(long long e) const
    {
        assert(e >= 0);
        Mod_Int a = *this, r = 1;
        for ( ; e; e >>= 1, a = a * a )
            if ( e & 1 )
                r = r * a;
        return r;
    }

    Mod_Int Inv() const
    {
        assert(v);
        return Pow(mod - 2);
    } // prime modulus

    Mod_Int operator/(Mod_Int b) const
    {
        return *this * b.Inv();
    }
};

template <int mod> struct Combination
{
    using Z = Mod_Int<mod>;
    vector<Z> fac{Z(1)}, ifac{Z(1)};

    Combination(int n = 0)
    {
        Init(n);
    }

    void Init(int n)
    {
        assert(0 <= n && n < mod);
        int old = (int)fac.size() - 1;
        if ( n <= old )
            return;
        fac.resize(n + 1);
        ifac.resize(n + 1);
        for ( int i = old + 1; i <= n; i++ )
            fac[i] = fac[i - 1] * i;
        ifac[n] = fac[n].Inv();
        for ( int i = n; i > old; i-- )
            ifac[i - 1] = ifac[i] * i;
    }

    Z Choose(int n, int k) const
    {
        if ( k < 0 || k > n )
            return 0;
        assert(n < (int)fac.size());
        return fac[n] * ifac[k] * ifac[n - k];
    }

    Z Permute(int n, int k) const
    {
        if ( k < 0 || k > n )
            return 0;
        assert(n < (int)fac.size());
        return fac[n] * ifac[n - k];
    }
};


template <int mod = 998244353> struct Set_Convolution
{
    static_assert(mod >= 2);
    using Z = Mod_Int<mod>;
    using Poly = vector<Z>;

    static void Transform(Poly &a, char op, bool invert = false)
    {
        assert(!a.empty() && a.size() <= INT_MAX);
        int n = a.size();
        assert((n & (n - 1)) == 0);
        assert(op == '|' || op == '&' || op == '^');
        assert(op != '^' || mod % 2 == 1);
        Z half = (mod + 1LL) / 2;
        for ( int len = 1; len < n; len *= 2 )
            for ( int i = 0; i < n; i += len * 2 )
                for ( int j = 0; j < len; j++ )
                {
                    Z &u = a[i + j], &v = a[i + j + len];
                    if ( op == '|' )
                        v = invert ? v - u : v + u;
                    else if ( op == '&' )
                        u = invert ? u - v : u + v;
                    else
                    {
                        Z x = u, y = v;
                        u = x + y;
                        v = x - y;
                        if ( invert )
                        {
                            u = u * half;
                            v = v * half;
                        }
                    }
                }
    }

    static Poly Multiply(Poly a, Poly b, char op)
    {
        assert(a.size() == b.size());
        Transform(a, op);
        Transform(b, op);
        for ( int i = 0; i < int(a.size()); i++ )
            a[i] = a[i] * b[i];
        Transform(a, op, true);
        return a;
    }
};


// BEGIN Subset_Convolution
// c[s] = sum_{t subset s} a[t] * b[s xor t].
template <int mod = 998244353>
vector<Mod_Int<mod>> Subset_Convolution(const vector<Mod_Int<mod>> &a,
                                        const vector<Mod_Int<mod>> &b)
{
    using F = Set_Convolution<mod>;
    using Poly = typename F::Poly;
    assert(!a.empty() && a.size() == b.size() && a.size() <= INT_MAX);
    int n = a.size(), m = 0;
    assert((n & (n - 1)) == 0);
    while ( (1 << m) < n )
        m++;
    vector<Poly> f(m + 1, Poly(n)), g(m + 1, Poly(n));
    vector<int> rank(n);
    for ( int s = 0; s < n; s++ )
    {
        rank[s] = __builtin_popcount(unsigned(s));
        f[rank[s]][s] = a[s];
        g[rank[s]][s] = b[s];
    }
    for ( int k = 0; k <= m; k++ )
    {
        F::Transform(f[k], '|');
        F::Transform(g[k], '|');
    }
    Poly answer(n), h(n);
    for ( int k = 0; k <= m; k++ )
    {
        fill(h.begin(), h.end(), 0);
        for ( int i = 0; i <= k; i++ )
            for ( int s = 0; s < n; s++ )
                h[s] = h[s] + f[i][s] * g[k - i][s];
        F::Transform(h, '|', true);
        for ( int s = 0; s < n; s++ )
            if ( rank[s] == k )
                answer[s] = h[s];
    }
    return answer;
}

// END Subset_Convolution


int main()
{
    int m;
    scanf("%d", &m);
    int n = 1 << m;
    using F = Set_Convolution<998244353>;
    F::Poly a(n), b(n);
    for ( auto &x : a )
    {
        int v;
        scanf("%d", &v);
        x = v;
    }
    for ( auto &x : b )
    {
        int v;
        scanf("%d", &v);
        x = v;
    }
    for ( char op : string("|&^") )
    {
        auto c = F::Multiply(a, b, op);
        for ( int s = 0; s < n; s++ )
            printf("%d%c", c[s].v, s + 1 == n ? '\n' : ' ');
    }
}
