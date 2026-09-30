#include <bits/stdc++.h>
using namespace std;
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct Mod64
{
    using ull = unsigned long long;
    using u128 = __uint128_t;

    static ull mul(ull a, ull b, ull m) { return u128(a) * b % m; }

    static ull power(ull a, ull b, ull m)
    {
        assert(m);
        ull r = 1 % m;
        a %= m;
        for (; b; b >>= 1, a = mul(a, a, m))
            if (b & 1) r = mul(r, a, m);
        return r;
    }
};


struct Prime64 : Mod64
{
    static bool prime(ull n)
    {
        if (n < 2) return false;
        for (ull p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37})
            if (n % p == 0) return n == p;
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
            if (a % n == 0) continue;
            ull x = power(a, d, n);
            if (x == 1 || x == n - 1) continue;
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
            if (!ok) return false;
        }
        return true;
    }
};

#include <cassert>
#include <bits/stdc++.h>
using namespace std;

// BEGIN extended_gcd
__int128_t extended_gcd(__int128_t a, __int128_t b, __int128_t &x, __int128_t &y)
{
    using i128 = __int128_t;
    if (!b)
    {
        x = 1;
        y = 0;
        return a;
    }
    i128 d = extended_gcd(b, a % b, y, x);
    y -= a / b * x;
    return d;
}

// END extended_gcd

#include <cassert>

// BEGIN mod_inverse
long long mod_inverse(long long a, long long m)
{
    using i128 = __int128_t;
    assert(m > 0);
    a %= m;
    if (a < 0) a += m;
    i128 x, y;
    if (extended_gcd(a, m, x, y) != 1) return -1;
    return (x % m + m) % m;
}

// END mod_inverse

#include <cassert>

// BEGIN crt_merge
bool crt_merge(long long &r, long long &m, long long b, long long n)
{
    using ll = long long;
    using i128 = __int128_t;
    assert(m > 0 && n > 0);
    r %= m;
    if (r < 0) r += m;
    b %= n;
    if (b < 0) b += n;
    i128 x, y;
    ll g = (ll)extended_gcd(m, n, x, y);
    i128 diff = i128(b) - r;
    if (diff % g) return false;
    i128 q = n / g, k = (diff / g * x % q + q) % q, mod = i128(m) * q;
    if (mod > LLONG_MAX) throw overflow_error("CRT modulus");
    r = (r + i128(m) * k) % mod;
    m = (ll)mod;
    return true;
}

// END crt_merge

#include <cassert>
#include <bits/stdc++.h>
using namespace std;

// BEGIN floor_sum
__int128_t floor_sum(long long n, long long m, long long a, long long b)
{
    using ll = long long;
    using i128 = __int128_t;
    assert(n >= 0 && m > 0);
    i128 ans = 0;
    auto norm = [&](ll &v)
    {
        ll q = v / m;
        if (v % m < 0) --q;
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
        if (y < m) break;
        n = (ll)(y / m);
        b = (ll)(y % m);
        swap(a, m);
    }
    return ans;
}

// END floor_sum


// Compatibility entry; handbook components are classified independently.
namespace number_theory_detail
{
constexpr auto floor_sum_fn = floor_sum;
}

struct NumberTheory : Prime64
{
    using ll = long long;
    using i128 = __int128_t;

    static i128 exgcd(i128 a, i128 b, i128 &x, i128 &y)
    {
        return extended_gcd(a, b, x, y);
    }

    static ll inverse(ll a, ll m) { return mod_inverse(a, m); }

    static bool crt(ll &r, ll &m, ll b, ll n) { return crt_merge(r, m, b, n); }

    static i128 floor_sum(ll n, ll m, ll a, ll b)
    {
        return number_theory_detail::floor_sum_fn(n, m, a, b);
    }
};

struct PollardRho
{
    using ull = unsigned long long;
    using u128 = __uint128_t;
    mt19937_64 rng;

    PollardRho(ull seed = 712367821) : rng(seed) {}

    ull rho(ull n)
    {
        if (n % 2 == 0) return 2;
        for (;;)
        {
            ull c = rng() % (n - 1) + 1, x = rng() % n, y = x, d = 1;
            auto f = [&](ull v)
            {
                return (Mod64::mul(v, v, n) + u128(c)) % n;
            };
            // Retry bounded attempts; Las Vegas: only exact divisors returned.
            for (int i = 0; i < 200000 && d == 1; i++)
            {
                x = f(x);
                y = f(f(y));
                d = gcd(x > y ? x - y : y - x, n);
            }
            if (1 < d && d < n) return d;
        }
    }

    void split(ull n, vector<ull> &a)
    {
        if (n == 1) return;
        if (Prime64::prime(n))
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
        if (n) phi[1] = mu[1] = 1;
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
                if (p > n / i) break;
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

    ModInt(long long x = 0) : v((x % mod + mod) % mod) {}

    ModInt operator+(ModInt b) const { return ModInt((long long)v + b.v); }

    ModInt operator-(ModInt b) const { return ModInt((long long)v - b.v); }

    ModInt operator*(ModInt b) const { return ModInt(1LL * v * b.v); }

    ModInt pow(long long e) const
    {
        assert(e >= 0);
        ModInt a = *this, r = 1;
        for (; e; e >>= 1, a = a * a)
            if (e & 1) r = r * a;
        return r;
    }

    ModInt inv() const
    {
        assert(v);
        return pow(mod - 2);
    } // prime modulus

    ModInt operator/(ModInt b) const { return *this * b.inv(); }

    ModInt &operator+=(ModInt b) { return *this = *this + b; }

    ModInt &operator-=(ModInt b) { return *this = *this - b; }

    ModInt &operator*=(ModInt b) { return *this = *this * b; }

    ModInt &operator/=(ModInt b) { return *this = *this / b; }
};

template <int mod> struct Binomial
{
    using Z = ModInt<mod>;
    vector<Z> fac{Z(1)}, ifac{Z(1)};

    Binomial(int n = 0) { init(n); }

    void init(int n)
    {
        assert(0 <= n && n < mod);
        int old = (int)fac.size() - 1;
        if (n <= old) return;
        fac.resize(n + 1);
        ifac.resize(n + 1);
        for (int i = old + 1; i <= n; i++) fac[i] = fac[i - 1] * i;
        ifac[n] = fac[n].inv();
        for (int i = n; i > old; i--) ifac[i - 1] = ifac[i] * i;
    }

    Z choose(int n, int k) const
    {
        if (k < 0 || k > n) return 0;
        assert(n < (int)fac.size());
        return fac[n] * ifac[k] * ifac[n - k];
    }

    Z permute(int n, int k) const
    {
        if (k < 0 || k > n) return 0;
        assert(n < (int)fac.size());
        return fac[n] * ifac[n - k];
    }
};


template <int mod> struct GaussMod
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
        for (const auto &v : a) assert((int)v.size() == n + 1);
        for (int col = 0; col < n && row < m; col++)
        {
            int p = row;
            while (p < m && !a[p][col].v) ++p;
            if (p == m) continue;
            swap(a[p], a[row]);
            Z inv = a[row][col].inv();
            for (int j = col; j <= n; j++) a[row][j] = a[row][j] * inv;
            for (int i = 0; i < m; i++)
                if (i != row && a[i][col].v)
                {
                    Z f = a[i][col];
                    for (int j = col; j <= n; j++) a[i][j] = a[i][j] - f * a[row][j];
                }
            where[col] = row++;
        }
        for (int i = row; i < m; i++)
            if (a[i][n].v) return {false, row, {}, {}};
        Solution ans{true, row, vector<Z>(n), {}};
        for (int j = 0; j < n; j++)
            if (where[j] != -1) ans.particular[j] = a[where[j]][n];
        for (int j = 0; j < n; j++)
            if (where[j] == -1)
            {
                vector<Z> v(n);
                v[j] = 1;
                for (int k = 0; k < n; k++)
                    if (where[k] != -1) v[k] = Z(0) - a[where[k]][j];
                ans.kernel.push_back(v);
            }
        return ans;
    }
};


// BEGIN det_prime
template <int mod> ModInt<mod> det_prime(vector<vector<ModInt<mod>>> a)
{
    using Z = ModInt<mod>;
    int n = (int)a.size();
    Z ans = 1;
    for (int i = 0; i < n; i++)
    {
        assert((int)a[i].size() == n);
        int p = i;
        while (p < n && !a[p][i].v) ++p;
        if (p == n) return 0;
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
            for (int k = i; k < n; k++) a[j][k] = a[j][k] - f * a[i][k];
        }
    }
    return ans;
}

// END det_prime


template <int mod> struct ModMatrix
{
    using Z = ModInt<mod>;
    using Matrix = vector<vector<Z>>;

    static Matrix multiply(const Matrix &a, const Matrix &b)
    {
        assert(!a.empty() && !b.empty());
        int n = a.size(), m = b[0].size(), k = b.size();
        assert((int)a[0].size() == k);
        Matrix c(n, vector<Z>(m));
        for (int i = 0; i < n; i++)
            for (int t = 0; t < k; t++)
                for (int j = 0; j < m; j++) c[i][j] = c[i][j] + a[i][t] * b[t][j];
        return c;
    }

    static Matrix power(Matrix a, unsigned long long e)
    {
        int n = a.size();
        assert(n > 0 && (int)a[0].size() == n);
        Matrix r(n, vector<Z>(n));
        for (int i = 0; i < n; i++) r[i][i] = 1;
        for (; e; e >>= 1, a = multiply(a, a))
            if (e & 1) r = multiply(r, a);
        return r;
    }
};


// Compatibility entry for existing drivers; the handbook uses separate modules.
template <int mod> struct LinearAlgebra : GaussMod<mod>, ModMatrix<mod>
{
    using Z = ModInt<mod>;
    using Matrix = vector<vector<Z>>;

    static Z determinant(Matrix a) { return det_prime<mod>(move(a)); }

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
        for (auto &row : lap) row.pop_back();
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
        if (n <= limit) return pmu[n];
        if (mmu.count(n)) return mmu[n];
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
        if (n <= limit) return pphi[n];
        if (mphi.count(n)) return mphi[n];
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
        if (m == 1 || b == 1) return 0;
        if (a == 1) return -1;
        ll offset = 0, k = 1;
        for (ll g; (g = gcd(a, m)) > 1;)
        {
            if (b == k) return offset;
            if (b % g) return -1;
            b /= g;
            m /= g;
            k = (__int128)k * (a / g) % m;
            ++offset;
        }
        ll target = (__int128)b * mod_inverse(k, m) % m;
        ll step = sqrtl(m) + 1;
        unordered_map<ll, ll> baby;
        baby.reserve(step);
        ll cur = 1 % m;
        for (ll j = 0; j < step; j++)
        {
            if (!baby.count(cur)) baby[cur] = j;
            cur = (__int128)cur * a % m;
        }
        ll inv = mod_inverse(Mod64::power(a, step, m), m);
        cur = target;
        for (ll i = 0; i <= step; i++)
        {
            auto it = baby.find(cur);
            if (it != baby.end()) return offset + i * step + it->second;
            cur = (__int128)cur * inv % m;
        }
        return -1;
    }
};


// BEGIN linear_congruence
pair<long long, long long> linear_congruence(long long a, long long b, long long m)
{
    assert(m > 0);
    using i128 = __int128_t;
    a %= m;
    if (a < 0) a += m;
    i128 x, y;
    i128 g = extended_gcd(a, m, x, y);
    if (i128(b) % g) return {-1, -1};
    i128 period = m / g;
    x = x * (-i128(b) / g) % period;
    if (x < 0) x += period;
    return {(long long)x, (long long)period};
}

// END linear_congruence


struct KthResidue
{
    using ll = long long;
    ll first, ratio, count;

    // Prime p <= 1e12; g is a primitive root of p; k > 0.
    // All roots: first * ratio^i mod p, 0 <= i < count.
    static optional<KthResidue> solve(ll a, unsigned long long k, ll p, ll g)
    {
        assert(p >= 2 && p <= 1000000000000LL && g >= 1 && g < p && k > 0);
        a %= p;
        if (a < 0) a += p;
        if (a == 0) return KthResidue{0, 1, 1};
        ll logarithm = DiscreteLog::solve(g, a, p);
        if (logarithm < 0) return nullopt;
        auto [exponent, period] = linear_congruence(k % (p - 1), -logarithm, p - 1);
        if (exponent < 0) return nullopt;
        ll first = Mod64::power(g, exponent, p);
        ll ratio = Mod64::power(g, period, p);
        return KthResidue{first, ratio, (p - 1) / period};
    }
};


struct PrimePowerRoots
{
    using ll = long long;
    ll first = 0, step = 1, lifts = 1;
    array<ll, 2> ratio{1, 1}, count{1, 1};

    ll size() const { return count[0] * count[1] * lifts; }

    ll get(ll i, ll j, ll lift) const
    {
        assert(i >= 0 && i < count[0] && j >= 0 && j < count[1]);
        assert(lift >= 0 && lift < lifts);
        ll x = (__int128)first * Mod64::power(ratio[0], i, step) % step;
        x = (__int128)x * Mod64::power(ratio[1], j, step) % step;
        return x + lift * step;
    }

    // p prime, 1 <= e, p^e <= 1e12, k > 0.
    // For odd p, g must be a primitive root modulo p^e. For p=2, g is unused.
    static optional<PrimePowerRoots>
    solve(ll a, unsigned long long k, ll p, int e, ll g = 0)
    {
        assert(p >= 2 && p <= 1000000000000LL && e >= 1 && e <= 39 && k > 0);
        array<ll, 40> power{1};
        for (int i = 1; i <= e; i++)
        {
            assert(power[i - 1] <= 1000000000000LL / p);
            power[i] = power[i - 1] * p;
        }
        ll mod = power[e];
        a %= mod;
        if (a < 0) a += mod;
        PrimePowerRoots answer;
        if (a == 0)
        {
            answer.step = power[(e - 1) / k + 1];
            answer.lifts = mod / answer.step;
            return answer;
        }
        int t = 0;
        while (a % p == 0)
        {
            a /= p;
            ++t;
        }
        if (t % k) return nullopt;
        ll scale = power[t / k], q = power[e - t];
        answer.first = 1;
        answer.step = scale * q;
        answer.lifts = mod / answer.step;
        auto cyclic = [&](ll base, ll target, ll order, int slot)
        {
            ll logarithm = DiscreteLog::solve(base, target, q);
            if (logarithm < 0) return false;
            auto [x, period] = linear_congruence(k % order, -logarithm, order);
            if (x < 0) return false;
            answer.first = (__int128)answer.first * Mod64::power(base, x, q) % q;
            answer.ratio[slot] = Mod64::power(base, period, q);
            answer.count[slot] = order / period;
            return true;
        };
        if (p != 2)
        {
            assert(g >= 1 && g < mod);
            if (!cyclic(g % q, a, q / p * (p - 1), 0)) return nullopt;
        }
        else if (q >= 4)
        {
            int sign = a % 4 == 3;
            auto [x, period] = linear_congruence(k % 2, -sign, 2);
            if (x < 0) return nullopt;
            answer.first = x ? q - 1 : 1;
            answer.ratio[0] = period == 1 ? q - 1 : 1;
            answer.count[0] = 2 / period;
            if (q >= 8 && !cyclic(5, sign ? q - a : a, q / 4, 1)) return nullopt;
        }
        answer.first *= scale;
        return answer;
    }
};


// BEGIN root_factors
vector<tuple<long long, int, long long>> root_factors(long long mod, PollardRho &rho)
{
    assert(mod >= 1 && mod <= 1000000000000LL);
    auto primes = rho.factor(mod);
    vector<tuple<long long, int, long long>> answer;
    for (int i = 0; i < (int)primes.size();)
    {
        long long p = primes[i], power = 1;
        int e = 0;
        while (i < (int)primes.size() && primes[i] == (unsigned long long)p)
        {
            power *= p;
            ++e;
            ++i;
        }
        long long g = 0;
        if (p != 2)
        {
            long long phi = power / p * (p - 1);
            auto factors = rho.factor(phi);
            factors.erase(unique(factors.begin(), factors.end()), factors.end());
            auto primitive = [&](long long candidate)
            {
                if (candidate % p == 0) return false;
                for (auto q : factors)
                    if (Mod64::power(candidate, phi / q, power) == 1) return false;
                return true;
            };
            g = 2;
            while (!primitive(g)) ++g;
        }
        answer.push_back({p, e, g});
    }
    return answer;
}

// END root_factors


struct CompositeRoots
{
    using ll = long long;
    ll mod = 1, total = 1;
    vector<PrimePowerRoots> parts;
    vector<ll> weight;

    ll get(ll index) const
    {
        assert(index >= 0 && index < total);
        ll answer = 0;
        for (int t = 0; t < (int)parts.size(); t++)
        {
            const auto &p = parts[t];
            ll local = index % p.size();
            index /= p.size();
            ll lift = local % p.lifts;
            local /= p.lifts;
            ll j = local % p.count[1], i = local / p.count[1];
            ll root = p.get(i, j, lift);
            answer = (answer + (__int128)root * weight[t]) % mod;
        }
        return answer;
    }

    // Factors are distinct primes with positive exponents: (p, e, g).
    // Odd-prime g is a primitive root modulo p^e; for p=2 use g=0.
    static optional<CompositeRoots>
    solve(ll a, unsigned long long k, const vector<tuple<ll, int, ll>> &factors)
    {
        assert(k > 0);
        CompositeRoots answer;
        for (auto [p, e, g] : factors)
        {
            auto roots = PrimePowerRoots::solve(a, k, p, e, g);
            if (!roots) return nullopt;
            ll m = roots->step * roots->lifts;
            assert(gcd(answer.mod, m) == 1);
            assert(answer.mod <= 1000000000000LL / m);
            answer.mod *= m;
            answer.total *= roots->size();
            answer.parts.push_back(*roots);
        }
        for (const auto &p : answer.parts)
        {
            ll m = p.step * p.lifts, rest = answer.mod / m;
            ll inverse = mod_inverse(rest % m, m);
            answer.weight.push_back((__int128)rest * inverse % answer.mod);
        }
        return answer;
    }

    static optional<CompositeRoots>
    solve(ll a, unsigned long long k, ll mod, PollardRho &rho)
    {
        return solve(a, k, root_factors(mod, rho));
    }
};

#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    PollardRho rho;
    while (t--)
    {
        unsigned long long n;
        long long m, k;
        cin >> n >> m >> k;
        auto f = root_factors(m, rho);
        vector<long long> a;
        if (f.size() == 1)
        {
            auto [p, e, g] = f[0];
            if (e == 1)
            {
                auto r = KthResidue::solve(k, n, p, p == 2 ? 1 : g);
                if (r)
                {
                    long long x = r->first;
                    for (long long i = 0; i < r->count; i++)
                    {
                        a.push_back(x);
                        x = (__int128)x * r->ratio % p;
                    }
                }
            }
            else
            {
                auto r = PrimePowerRoots::solve(k, n, p, e, g);
                if (r)
                    for (long long i = 0; i < r->count[0]; i++)
                        for (long long j = 0; j < r->count[1]; j++)
                            for (long long z = 0; z < r->lifts; z++)
                                a.push_back(r->get(i, j, z));
            }
        }
        else
        {
            auto r = CompositeRoots::solve(k, n, f);
            if (r)
                for (long long i = 0; i < r->total; i++) a.push_back(r->get(i));
        }
        sort(a.begin(), a.end());
        cout << a.size() << '\n';
        if (!a.empty())
        {
            for (int i = 0; i < (int)a.size(); i++)
                cout << a[i] << (i + 1 == (int)a.size() ? '\n' : ' ');
        }
    }
    return 0;
}
