#include "../src/compact/polynomial_interpolation.hpp"
#include "../src/compact/fps_functions.hpp"
#include "../src/compact/chirp_z.hpp"
#include <iostream>

using P = MultipointEvaluation;
using V = P::Poly;
using ll = long long;
constexpr ll mod = 998244353;
int recoveries = 0, systems = 0, rejections = 0;

ll power(ll a, int k)
{
    ll r = 1;
    for (; k; k >>= 1, a = a * a % mod)
        if (k & 1) r = r * a % mod;
    return r;
}

ll horner(const V &f, ll x)
{
    ll a = 0;
    for (int i = int(f.size()) - 1; i >= 0; i--) a = (a * x + f[i].v) % mod;
    return a;
}

ll geometric(ll x, int n)
{
    if (x == 1) return n;
    return (power(x, n) + mod - 1) % mod * power((x + mod - 1) % mod, mod - 2) % mod;
}

void same(const V &a, const V &b)
{
    assert(a.size() == b.size());
    for (int i = 0; i < int(a.size()); i++) assert(a[i].v == b[i].v);
}

void check(const V &x, const V &y, const V &want)
{
    auto xs = x, ys = y;
    auto f = polynomial_interpolation(x, y);
    assert(f);
    same(*f, want);
    same(x, xs);
    same(y, ys);
    recoveries++;
}

void reject(const V &x, const V &y)
{
    auto xs = x, ys = y;
    assert(!polynomial_interpolation(x, y));
    same(x, xs);
    same(y, ys);
    rejections++;
}

void recover(const V &x, V f)
{
    assert(f.size() <= x.size());
    V y(x.size());
    for (int i = 0; i < int(x.size()); i++) y[i] = horner(f, x[i].v);
    f.resize(x.size());
    check(x, y, f);
}

V vandermonde(const V &x, const V &y)
{
    int n = x.size();
    vector<vector<ll>> a(n, vector<ll>(n + 1));
    for (int i = 0; i < n; i++)
    {
        ll value = 1;
        for (int j = 0; j < n; j++)
        {
            a[i][j] = value;
            value = value * x[i].v % mod;
        }
        a[i][n] = y[i].v;
    }
    for (int j = 0; j < n; j++)
    {
        int pivot = j;
        while (pivot < n && a[pivot][j] == 0) pivot++;
        assert(pivot < n);
        swap(a[j], a[pivot]);
        ll inverse = power(a[j][j], mod - 2);
        for (int k = j; k <= n; k++) a[j][k] = a[j][k] * inverse % mod;
        for (int i = 0; i < n; i++)
        {
            if (i == j) continue;
            ll value = a[i][j];
            for (int k = j; k <= n; k++)
                a[i][k] = (a[i][k] - value * a[j][k] % mod + mod) % mod;
        }
    }
    V f(n);
    for (int i = 0; i < n; i++) f[i] = a[i][n];
    systems++;
    return f;
}

V distinct(int n, mt19937 &rng)
{
    ll offset = rng() % mod, step = 1 + rng() % (mod - 1);
    V x(n);
    for (int i = 0; i < n; i++) x[i] = (offset + step * i) % mod;
    shuffle(x.begin(), x.end(), rng);
    return x;
}

void small()
{
    check({}, {}, {});
    reject({}, {1});
    reject({1}, {});
    reject({0, 1}, {7});
    reject({0}, {7, 8});
    reject({0, mod}, {1, 1});
    reject({-1, mod - 1}, {2, 3});
    reject({5, 5}, {0, 0});
    reject({0, 1, 2, 0}, {3, 4, 5, 6});
    for (ll x : {0LL, 1LL, -1LL, LLONG_MIN, LLONG_MAX})
        for (ll y : {0LL, 1LL, -1LL, LLONG_MIN, LLONG_MAX}) check({x}, {y}, {y});
    V points{0, 1, -1, 2, -2, 3, -3};
    for (int n = 0; n <= 7; n++)
        for (int mask = 0; mask < (1 << n); mask++)
        {
            V x(points.begin(), points.begin() + n), f(n);
            for (int i = 0; i < n; i++) f[i] = (mask >> i) & 1;
            recover(x, f);
        }
    recover({LLONG_MIN, LLONG_MAX, -1, 0, 1},
            {LLONG_MIN, LLONG_MAX, -998244354LL, 998244354LL, -7});
    mt19937 rng(212131072);
    for (int t = 0; t < 800; t++)
    {
        int n = rng() % 13;
        V x = distinct(n, rng), y(n);
        for (auto &v : y) v = rng() % mod;
        check(x, y, vandermonde(x, y));
    }
    for (int t = 0; t < 1000; t++)
    {
        int n = rng() % 101;
        V x = distinct(n, rng), f(n);
        for (auto &v : f) v = rng() % mod;
        if (t % 3 == 0) f.resize(n / 2);
        if (t % 5 == 0) fill(f.begin(), f.end(), P::Z(0));
        recover(x, f);
        if (n > 1 && t % 4 == 0)
        {
            x.back() = x[0];
            reject(x, V(n));
        }
    }
    for (int n : {0, 1, 2, 3, 7, 8, 9, 31, 32, 33, 127, 128, 129, 257, 513})
    {
        V x = distinct(n, rng), f(n);
        for (auto &v : f) v = rng() % mod;
        recover(x, f);
        recover(x, {});
        if (n) recover(x, {23});
    }
    reject(V(1025, 17), V(1025));
    V x = distinct(2049, rng);
    x.back() = x[1024];
    reject(x, V(2049, 19));
    cout << "Small: " << recoveries << " coefficient recoveries, " << systems
         << " independent Vandermonde systems, " << rejections
         << " explicit rejections PASS" << endl;
}

V large_points(int n)
{
    // A permutation of consecutive field elements: distinct, with 0, 1 and -1.
    V x(n);
    for (int i = 0; i < n; i++) x[i] = i - n / 2;
    mt19937 rng(21265537 + n);
    shuffle(x.begin(), x.end(), rng);
    return x;
}

void large_dense(bool alternating)
{
    constexpr int n = 131072;
    V x = large_points(n), y(n), f(n, 1);
    for (int i = 0; i < n; i++)
    {
        ll point = alternating ? (mod - x[i].v) % mod : x[i].v;
        y[i] = geometric(point, n);
        if (alternating && i % 2) f[i] = -1;
    }
    check(x, y, f);
    cout << "Large " << (alternating ? "alternating" : "dense")
         << ": 131072 points, independent geometric closed form PASS" << endl;
}

void large_sparse()
{
    constexpr int n = 65537;
    V x = large_points(n), y(n), f(n);
    f[0] = 13;
    f[12345] = -7;
    f[n - 1] = 19;
    for (int i = 0; i < n; i++)
        y[i] = (13 + (mod - 7) * power(x[i].v, 12345) % mod +
                19 * power(x[i].v, n - 1)) % mod;
    check(x, y, f);
    cout << "Large sparse: 65537 points, independent high-degree monomial sum PASS"
         << endl;
}

void large_flat(bool zero)
{
    int n = zero ? 65535 : 131072;
    V x = large_points(n), y(n, zero ? 0 : 7654321), f(n);
    f[0] = y[0];
    check(x, y, f);
    cout << "Large " << (zero ? "zero" : "constant") << ": " << n
         << " points, all high coefficient zeros preserved PASS" << endl;
}

void composition()
{
    V x{0, 1, 2, 4, 8}, f{5, 7, 11, 13, 17};
    recover(x, f);
    const P tree({0, 1, 1, 2});
    auto a = tree.evaluate(f);
    for (int i = 0; i < 4; i++) assert(a[i].v == horner(f, V{0, 1, 1, 2}[i].v));
    reject({0, 1, 1, 2}, a);
    auto c = chirp_z(f, P::Z(1), P::Z(2), 4);
    for (int i = 0; i < 4; i++) assert(c[i].v == horner(f, 1 << i));
    auto [q, r] = PolynomialDivision::divide(f, {0, 0, 1});
    same(q, {11, 13, 17});
    same(r, {5, 7});
    same(FpsFunctions::derivative(f), {7, 22, 39, 68});
    same(FpsInverse::inverse({1, -1}, 5), {1, 1, 1, 1, 1});
    recover(x, f);
    cout << "Composition: evaluation still permits duplicates; division, FPS and "
            "chirp_z coexist PASS" << endl;
}

int main(int argc, char **argv)
{
    string mode = argc == 1 ? "all" : argv[1];
    assert(mode == "all" || mode == "small" || mode == "dense" ||
           mode == "alternating" || mode == "sparse" || mode == "zero" ||
           mode == "constant" || mode == "composition");
    if (mode == "all" || mode == "small") small();
    if (mode == "all" || mode == "dense") large_dense(false);
    if (mode == "all" || mode == "alternating") large_dense(true);
    if (mode == "all" || mode == "sparse") large_sparse();
    if (mode == "all" || mode == "zero") large_flat(true);
    if (mode == "all" || mode == "constant") large_flat(false);
    if (mode == "all" || mode == "composition") composition();
}
