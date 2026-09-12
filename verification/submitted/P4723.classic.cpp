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


template <int mod, int primitive = 3> struct Ntt_Convolution
{
    static_assert(mod >= 2 && primitive >= 1 && primitive < mod);
    static constexpr int max_size = (mod - 1) & -(mod - 1);
    using Z = Mod_Int<mod>;
    using Poly = vector<Z>;

    // mod is prime, primitive is a primitive root modulo mod.
    static void Ntt(Poly &a, bool invert = false)
    {
        int n = a.size();
        assert(n > 0 && (n & (n - 1)) == 0 && n <= max_size);
        for ( int i = 1, j = 0; i < n; i++ )
        {
            int bit = n >> 1;
            for ( ; j & bit; bit >>= 1 )
                j ^= bit;
            j ^= bit;
            if ( i < j )
                swap(a[i], a[j]);
        }
        for ( int half = 1; half < n; half *= 2 )
        {
            int len = half * 2;
            Z step = Z(primitive).Pow((mod - 1) / len);
            if ( invert )
                step = step.Inv();
            for ( int i = 0; i < n; i += len )
            {
                Z w = 1;
                for ( int j = 0; j < half; j++ )
                {
                    Z u = a[i + j], v = a[i + j + half] * w;
                    a[i + j] = u + v;
                    a[i + j + half] = u - v;
                    w = w * step;
                }
            }
        }
        if ( invert )
        {
            Z inverse = Z(n).Inv();
            for ( auto &x : a )
                x = x * inverse;
        }
    }

    static Poly Multiply(Poly a, Poly b)
    {
        if ( a.empty() || b.empty() )
            return {};
        assert(a.size() + b.size() - 1 <= max_size);
        int size = a.size() + b.size() - 1, n = 1;
        while ( n < size )
            n *= 2;
        a.resize(n);
        b.resize(n);
        Ntt(a);
        Ntt(b);
        for ( int i = 0; i < n; i++ )
            a[i] = a[i] * b[i];
        Ntt(a, true);
        a.resize(size);
        return a;
    }
};


template <int mod = 998244353, int primitive = 3> struct Bostan_Mori
{
    using N = Ntt_Convolution<mod, primitive>;
    using Z = typename N::Z;
    using Poly = typename N::Poly;
    using U = unsigned long long;

    // Coefficient of x^n in p(x) / q(x), with q[0] != 0.
    static Z Coefficient(Poly p, Poly q, U n)
    {
        assert(!q.empty() && q[0].v != 0);
        assert(max(p.size(), q.size()) <= (N::max_size + 1ULL) / 2);
        while ( n && !p.empty() )
        {
            Poly r = q;
            for ( int i = 1; i < int(r.size()); i += 2 )
                r[i] = Z(0) - r[i];
            Poly a = N::Multiply(p, r);
            Poly b = N::Multiply(q, r);
            p.clear();
            q.clear();
            for ( int i = n & 1; i < int(a.size()); i += 2 )
                p.push_back(a[i]);
            for ( int i = 0; i < int(b.size()); i += 2 )
                q.push_back(b[i]);
            n >>= 1;
        }
        return p.empty() ? Z(0) : p[0] / q[0];
    }

    // a[i] = c[0]*a[i-1] + ... + c[k-1]*a[i-k], for i >= k.
    static Z Recurrence(const Poly &init, const Poly &c, U n)
    {
        assert(init.size() == c.size());
        int k = c.size();
        if ( k == 0 )
            return 0;
        if ( n < init.size() )
            return init[n];
        assert(k + 1ULL <= (N::max_size + 1ULL) / 2);
        Poly q(k + 1);
        q[0] = 1;
        for ( int i = 0; i < k; i++ )
            q[i + 1] = Z(0) - c[i];
        Poly p = N::Multiply(init, q);
        p.resize(k);
        return Coefficient(p, q, n);
    }
};


int main()
{
    unsigned long long n;
    int k;
    scanf("%llu%d", &n, &k);
    using B = Bostan_Mori<>;
    B::Poly c(k), init(k);
    for ( auto &x : c )
    {
        int v;
        scanf("%d", &v);
        x = v;
    }
    for ( auto &x : init )
    {
        int v;
        scanf("%d", &v);
        x = v;
    }
    printf("%d\n", B::Recurrence(init, c, n).v);
}
