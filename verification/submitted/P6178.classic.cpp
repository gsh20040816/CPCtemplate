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


template <int mod> struct Matrix_Tree
{
    using A = Linear_Algebra<mod>;
    using Z = typename A::Z;
    using Edge = tuple<int, int, Z>;
    enum class Kind
    {
        undirected,
        toward_root,
        away_from_root
    };

    // Sum of products of edge weights; vertices 0..n-1, prime modulus.
    static Z Count(int n, const vector<Edge> &edges, int root, Kind kind)
    {
        assert(n >= 1 && root >= 0 && root < n);
        typename A::Matrix lap(n - 1, vector<Z>(n - 1));
        auto add = [&](int u, int v, Z w)
        {
            if ( u == root )
                return;
            int i = u - (u > root), j = v - (v > root);
            lap[i][i] = lap[i][i] + w;
            if ( v != root )
                lap[i][j] = lap[i][j] - w;
        };
        for ( auto [u, v, w] : edges )
        {
            assert(u >= 0 && u < n && v >= 0 && v < n);
            if ( u == v )
                continue;
            if ( kind == Kind::away_from_root )
                swap(u, v);
            add(u, v, w);
            if ( kind == Kind::undirected )
                add(v, u, w);
        }
        return A::Determinant(lap);
    }
};


int main()
{
    using M = Matrix_Tree<1000000007>;
    int n, m, type;
    scanf("%d%d%d", &n, &m, &type);
    vector<M::Edge> edges;
    for ( int i = 0; i < m; i++ )
    {
        int u, v;
        long long w;
        scanf("%d%d%lld", &u, &v, &w);
        edges.push_back({u - 1, v - 1, w});
    }
    auto kind = type ? M::Kind::away_from_root : M::Kind::undirected;
    printf("%d\n", M::Count(n, edges, 0, kind).v);
}
