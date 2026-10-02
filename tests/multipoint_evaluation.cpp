#include "../src/compact/multipoint_evaluation.hpp"
#include "../src/compact/fps_functions.hpp"
#include "../src/compact/chirp_z.hpp"
#include <iostream>

using P = MultipointEvaluation;
using V = P::Poly;
using ll = long long;
constexpr ll mod = 998244353;
int checks = 0;

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

void check(const P &tree, const V &f, const V &x)
{
    V saved = f;
    auto a = tree.evaluate(f);
    same(f, saved);
    assert(a.size() == x.size());
    for (int i = 0; i < int(x.size()); i++) assert(a[i].v == horner(f, x[i].v));
    checks++;
}

void check_tree(const P &tree, const V &x)
{
    if (x.empty()) return;
    vector<ll> a{1};
    for (auto v : x)
    {
        vector<ll> b(a.size() + 1);
        for (int i = 0; i < int(a.size()); i++)
        {
            b[i] = (b[i] - a[i] * v.v % mod + mod) % mod;
            b[i + 1] = (b[i + 1] + a[i]) % mod;
        }
        a = move(b);
    }
    assert(tree.p[1].size() == a.size());
    for (int i = 0; i < int(a.size()); i++) assert(tree.p[1][i].v == a[i]);
}

void small()
{
    V fixed{0, 1, -1, 2, 2, mod - 1, 7, 0};
    const P fixed_tree(fixed);
    for (int n = 0; n <= 7; n++)
        for (int mask = 0; mask < (1 << n); mask++)
        {
            V f(n);
            for (int i = 0; i < n; i++) f[i] = (mask >> i) & 1;
            check(fixed_tree, f, fixed);
        }
    check(fixed_tree, {LLONG_MIN, LLONG_MAX, -998244354LL, 998244354LL}, fixed);
    mt19937 rng(622131072);
    for (int t = 0; t < 1800; t++)
    {
        int n = rng() % 100, m = rng() % 100;
        V f(n), x(m);
        for (auto &a : f) a = rng() % mod;
        for (auto &a : x) a = rng() % mod;
        if (t % 3 == 0)
            for (int i = 0; i < m; i++) x[i] = (i % 7) - 3;
        if (t % 5 == 0) fill(x.begin(), x.end(), P::Z(t % 11));
        if (t % 7 == 0) fill(f.begin(), f.end(), P::Z(0));
        if (t % 2 == 0) f.resize(n + 5);
        auto xs = x;
        const P tree(x);
        same(x, xs);
        check_tree(tree, x);
        auto saved = tree.p;
        check(tree, f, x);
        check(tree, {}, x);
        check(tree, {17, 0, 0}, x);
        check(tree, {1, 2, 3, 4}, x);
        check(tree, f, x);
        assert(tree.p.size() == saved.size());
        for (int i = 0; i < int(saved.size()); i++) same(tree.p[i], saved[i]);
        same(x, xs);
    }
    for (int n : {0, 1, 2, 3, 7, 8, 9, 31, 32, 33, 127, 128, 129, 257})
        for (int m : {0, 1, 2, 3, 7, 8, 9, 31, 32, 33, 127, 128, 129, 257})
        {
            V f(n), x(m);
            for (auto &a : f) a = rng() % mod;
            for (int i = 0; i < m; i++) x[i] = (i * 37) % 101;
            check(P(x), f, x);
        }
    cout << "Independent Horner: " << checks << " evaluations PASS" << endl;
}

void large_dense()
{
    constexpr int n = 131072;
    mt19937 rng(131072622);
    V x(n), f(n, 1);
    for (auto &a : x) a = rng() % mod;
    for (int i = 0; i < n; i += 1024)
    {
        x[i] = 0;
        x[i + 1] = 1;
        x[i + 2] = -1;
        x[i + 3] = x[i + 4];
    }
    auto xs = x;
    const P tree(x);
    auto a = tree.evaluate(f);
    assert(a.size() == x.size());
    for (int i = 0; i < n; i++)
    {
        assert(a[i].v == geometric(x[i].v, n));
        assert(f[i].v == 1);
    }
    for (int i = 1; i < n; i += 2) f[i] = -1;
    a = tree.evaluate(f);
    for (int i = 0; i < n; i++)
    {
        assert(a[i].v == geometric((mod - x[i].v) % mod, n));
        assert(f[i].v == (i % 2 ? mod - 1 : 1));
    }
    V short_f(17);
    for (auto &v : short_f) v = rng() % mod;
    check(tree, short_f, x);
    check(tree, {}, x);
    check(tree, {999, 0, 0}, x);
    same(x, xs);

    // Dense long dividend / short point set exercises root-level reduction.
    V few(x.begin(), x.begin() + 17);
    check(P(few), f, few);
    check(P({0}), f, {0});
    check(P({1}), f, {1});
    check(P({-1}), f, {-1});
    check(P({}), f, {});
    cout << "Large dense: 131072 geometric/alternating closed forms and asymmetric "
            "degrees PASS" << endl;
}

void large_repeated()
{
    constexpr int n = 131072;
    // All points coincide: legal even at the official maximum M.
    V repeated(n, 3), dense(n, 1);
    const P duplicates(repeated);
    auto a = duplicates.evaluate(dense);
    ll value = geometric(3, n);
    assert(a.size() == n);
    for (auto v : a) assert(v.v == value);
    for (auto v : repeated) assert(v.v == 3);
    for (auto v : dense) assert(v.v == 1);
    check(duplicates, {7, 0, 0}, repeated);
    cout << "Repeated points: 131072 equal points and dense polynomial PASS" << endl;
}

void large_sparse()
{
    // Unequal non-power-of-two dimensions, sparse high degree and trailing zeros.
    mt19937 rng(131072622);
    rng.discard(131072 + 17); // Keep the same corpus as the combined large run.
    V odd(65535), sparse(65537);
    for (auto &v : odd) v = rng() % mod;
    sparse[0] = 13;
    sparse[12345] = -7;
    sparse.back() = 19;
    const P uneven(odd);
    auto a = uneven.evaluate(sparse);
    for (int i = 0; i < int(odd.size()); i++)
    {
        ll want = (13 + (mod - 7) * power(odd[i].v, 12345) % mod +
                   19 * power(odd[i].v, 65536)) % mod;
        assert(a[i].v == want);
    }
    sparse.resize(131072);
    same(a, uneven.evaluate(sparse));
    cout << "Sparse: odd unequal dimensions, high degree and trailing zeros PASS" << endl;
}

void composition()
{
    V f{5, 7, 11, 13, 17}, x{0, 1, 2, 4, 8};
    const P tree(x);
    check(tree, f, x);
    auto a = chirp_z(f, P::Z(1), P::Z(2), 4);
    for (int i = 0; i < 4; i++) assert(a[i].v == horner(f, 1 << i));
    auto [q, r] = PolynomialDivision::divide(f, {0, 0, 1});
    same(q, {11, 13, 17});
    same(r, {5, 7});
    same(FpsFunctions::derivative(f), {7, 22, 39, 68});
    same(FpsInverse::inverse({1, -1}, 5), {1, 1, 1, 1, 1});
    check(tree, f, x);
    cout << "Shared translation unit: division, FPS and chirp_z PASS" << endl;
}

int main(int argc, char **argv)
{
    string mode = argc == 1 ? "all" : argv[1];
    assert(mode == "all" || mode == "small" || mode == "dense" ||
           mode == "repeated" || mode == "sparse" || mode == "composition");
    if (mode == "all" || mode == "small") small();
    if (mode == "all" || mode == "dense") large_dense();
    if (mode == "all" || mode == "repeated") large_repeated();
    if (mode == "all" || mode == "sparse") large_sparse();
    if (mode == "all" || mode == "composition") composition();
}
