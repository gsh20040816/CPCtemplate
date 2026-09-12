#include <cstdio>
#include <vector>
#include <cassert>
#include <climits>
#include <utility>
using namespace std;

struct FunctionalGraph
{
    using U = unsigned long long;
    int n;
    vector<int> component, position, entry, depth, order;
    vector<vector<int>> cycles, up;

    explicit FunctionalGraph(vector<int> to = {})
    {
        build(move(to));
    }

    void build(vector<int> to)
    {
        assert(to.size() <= INT_MAX);
        n = to.size();
        vector<int> degree(n);
        for (int v : to)
        {
            assert(0 <= v && v < n);
            degree[v]++;
        }
        order.clear();
        for (int u = 0; u < n; u++)
            if (degree[u] == 0)
                order.push_back(u);
        for (int i = 0; i < int(order.size()); i++)
        {
            int v = to[order[i]];
            if (--degree[v] == 0)
                order.push_back(v);
        }
        component.assign(n, -1);
        position.assign(n, -1);
        entry.resize(n);
        depth.assign(n, 0);
        cycles.clear();
        for (int u = 0; u < n; u++)
            if (degree[u] && component[u] == -1)
            {
                vector<int> cycle;
                int v = u, id = cycles.size();
                do
                {
                    component[v] = id;
                    position[v] = cycle.size();
                    entry[v] = v;
                    cycle.push_back(v);
                    v = to[v];
                } while (v != u);
                cycles.push_back(move(cycle));
            }
        for (int i = int(order.size()) - 1; i >= 0; i--)
        {
            int u = order[i], v = to[u];
            component[u] = component[v];
            entry[u] = entry[v];
            depth[u] = depth[v] + 1;
        }
        up.assign(1, to);
        for (int k = 1; (1ULL << k) <= U(n); k++)
        {
            vector<int> row(n);
            for (int u = 0; u < n; u++)
                row[u] = up[k - 1][up[k - 1][u]];
            up.push_back(move(row));
        }
    }

    int advance(int u, U k) const
    {
        assert(0 <= u && u < n);
        if (k >= U(depth[u]))
        {
            k -= depth[u];
            u = entry[u];
            const auto &cycle = cycles[component[u]];
            return cycle[(U(position[u]) + k % cycle.size()) % cycle.size()];
        }
        for (int bit = 0; k; bit++, k >>= 1)
            if (k & 1)
                u = up[bit][u];
        return u;
    }

    int steps(int u, int v) const
    {
        assert(0 <= u && u < n && 0 <= v && v < n);
        if (component[u] != component[v] || depth[u] < depth[v])
            return -1;
        if (depth[v] > 0)
        {
            int d = depth[u] - depth[v];
            return advance(u, d) == v ? d : -1;
        }
        int offset = position[v] - position[entry[u]];
        if (offset < 0)
            offset += int(cycles[component[u]].size());
        return depth[u] + offset;
    }
};

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
    vector<Z> fac{Z(1)}, ifac{Z(1)};

    Binomial(int n = 0)
    {
        init(n);
    }

    void init(int n)
    {
        assert(0 <= n && n < mod);
        int old = (int)fac.size() - 1;
        if (n <= old)
            return;
        fac.resize(n + 1);
        ifac.resize(n + 1);
        for (int i = old + 1; i <= n; i++)
            fac[i] = fac[i - 1] * i;
        ifac[n] = fac[n].inv();
        for (int i = n; i > old; i--)
            ifac[i - 1] = ifac[i] * i;
    }

    Z choose(int n, int k) const
    {
        if (k < 0 || k > n)
            return 0;
        assert(n < (int)fac.size());
        return fac[n] * ifac[k] * ifac[n - k];
    }

    Z permute(int n, int k) const
    {
        if (k < 0 || k > n)
            return 0;
        assert(n < (int)fac.size());
        return fac[n] * ifac[n - k];
    }
};


int main()
{
    int tests;
    scanf("%d", &tests);
    using Z = ModInt<1000000007>;
    Binomial<1000000007> factorial;
    FunctionalGraph graph;
    while (tests--)
    {
        int n;
        scanf("%d", &n);
        vector<int> a(n), b(n), w(n);
        for (auto &x : a)
            scanf("%d", &x);
        for (auto &x : b)
        {
            scanf("%d", &x);
            x--;
        }
        for (auto &x : w)
            scanf("%d", &x);
        vector<char> certain(n);
        for (int u = 0; u < n; u++)
        {
            int v = b[u];
            if (a[u] < a[v])
            {
                certain[u] = true;
                b[u] = u;
            }
            else if (a[u] >= a[v] + 1LL * w[v])
                b[u] = u;
        }
        graph.build(move(b));
        factorial.init(n);
        for (int u = 0; u < n; u++)
        {
            Z probability = 0;
            if (certain[graph.entry[u]])
                probability = factorial.ifac[graph.depth[u] + 1];
            Z answer = Z(a[u]) + Z(w[u]) * probability;
            printf("%d%c", answer.v, u + 1 == n ? '\n' : ' ');
        }
    }
}
