#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
using namespace std;
using B = boost::multiprecision::cpp_int;
#include "../src/compact/real_polar.hpp"
#ifdef REAL_POLAR_TYPE_PROBES
#include "real-polar-type-probes.hpp"
#endif

struct Dyadic { B m; int k; };
Dyadic multiply(Dyadic a, Dyadic b) { return {a.m * b.m, a.k + b.k}; }
Dyadic add(Dyadic a, Dyadic b)
{
    int k = min(a.k, b.k);
    return {(a.m << (a.k - k)) + (b.m << (b.k - k)), k};
}
int compare(Dyadic a, Dyadic b)
{
    int k = min(a.k, b.k);
    B x = a.m << (a.k - k), y = b.m << (b.k - k);
    return (x > y) - (x < y);
}
struct ExactPoint { Dyadic x, y; };
int exact_cross(ExactPoint a, ExactPoint b)
{
    return compare(multiply(a.x, b.y), multiply(a.y, b.x));
}
bool exact_less(ExactPoint a, ExactPoint b)
{
    bool az = a.x.m == 0 && a.y.m == 0, bz = b.x.m == 0 && b.y.m == 0;
    if (az || bz) return az && !bz;
    auto half = [](ExactPoint a) { return a.y.m < 0 || (a.y.m == 0 && a.x.m < 0); };
    if (half(a) != half(b)) return half(a) < half(b);
    int c = exact_cross(a, b);
    if (c) return c > 0;
    auto norm = [](ExactPoint a) { return add(multiply(a.x, a.x), multiply(a.y, a.y)); };
    return compare(norm(a), norm(b)) < 0;
}

template<class C> void run(const char *label, int mode)
{
    using R = typename C::R;
    using P = typename C::P;
    constexpr int p = numeric_limits<R>::digits;
    constexpr int lo = numeric_limits<R>::min_exponent - p;
    constexpr int hi = numeric_limits<R>::max_exponent - p;
    uint64_t mmax = uint64_t(~uint64_t(0)) >> (64 - p);
    mt19937_64 rng(18760427 + p);
    struct Value { R value; Dyadic exact; };
    auto scalar = [&](uint64_t m, int k, int sign)
    {
        R v = ldexp(R(m), k);
        assert(isfinite(v));
        if (m) assert(v != 0);
        if (sign < 0) v = -v;
        return Value{v, {B(m) * sign, k}};
    };
    vector<Value> special;
    for (int k : {lo, lo + 1, -p, 0, hi - 1, hi})
        for (uint64_t m : {uint64_t(0), uint64_t(1), uint64_t(2), (mmax >> 1),
                           (mmax >> 1) + 1, mmax - 1, mmax})
            for (int sign : {-1, 1}) special.push_back(scalar(m, k, sign));
    vector<P> points;
    vector<ExactPoint> exact;
    auto append = [&](Value x, Value y) { points.push_back({x.value, y.value}); exact.push_back({x.exact, y.exact}); };
    auto zero = scalar(0, 0, 1);
    for (auto a : special)
    {
        append(a, zero); append(zero, a); append(a, a);
    }
    for (int i = 0; i < 2000; i++)
    {
        auto random_value = [&]()
        {
            int k = lo + rng() % (hi - lo + 1);
            uint64_t m = rng() & mmax;
            return scalar(m, k, rng() & 1 ? -1 : 1);
        };
        append(random_value(), random_value());
    }
    // Mixed coordinate exponents must not lose the tiny coordinate by rescaling.
    vector<Value> extremes;
    for (int sign : {-1, 1})
        for (auto [m, k] : {pair<uint64_t, int>{1, lo}, {2, lo}, {mmax, lo}, {mmax, hi}, {1, 0}})
            extremes.push_back(scalar(m, k, sign));
    for (auto x : extremes) for (auto y : extremes) append(x, y);
    int near_begin = int(points.size());
    // Consecutive near-parallel integer directions with determinant exactly +/-1.
    for (int k : {lo, -p, hi})
        for (int sx : {-1, 1})
            for (int sy : {-1, 1})
            {
                append(scalar(mmax, k, sx), scalar(mmax - 1, k, sy));
                append(scalar(mmax - 1, k, sx), scalar(mmax - 2, k, sy));
            }
    long long pairs = 0;
    auto check_pair = [&](int i, int j)
    {
        assert(C::cross_sign(points[i], points[j]) == exact_cross(exact[i], exact[j]));
        assert(C{}(points[i], points[j]) == exact_less(exact[i], exact[j]));
        ++pairs;
    };
    // Exhaustively compare all constructed boundaries plus explicit close cases.
    int boundaries = int(special.size()) * 3;
    for (int i = 0; i < boundaries; i++)
        for (int j = 0; j < boundaries; j++) check_pair(i, j);
    for (int i = near_begin - int(extremes.size() * extremes.size()); i < int(points.size()); i++)
        for (int j = near_begin - int(extremes.size() * extremes.size()); j < int(points.size()); j++)
            check_pair(i, j);
    for (int i = 0; i < 30000; i++) check_pair(rng() % points.size(), rng() % points.size());
    vector<P> grid;
    for (R x : {R(-2), R(-1), R(-0.0), R(0), R(1), R(2)})
        for (R y : {R(-2), R(-1), R(-0.0), R(0), R(1), R(2)}) grid.push_back({x,y});
    auto order_check = [&](P a, P b, P c)
    {
        assert(!C{}(a, a));
        assert(!(C{}(a, b) && C{}(b, a)));
        if (C{}(a, b) && C{}(b, c)) assert(C{}(a, c));
        if (!C{}(a, b) && !C{}(b, a) && !C{}(b, c) && !C{}(c, b))
            assert(!C{}(a, c) && !C{}(c, a));
    };
    for (P a : grid) for (P b : grid) for (P c : grid) order_check(a,b,c);
    for (int i = 0; i < 100000; i++)
        order_check(points[rng()%points.size()], points[rng()%points.size()], points[rng()%points.size()]);
    vector<int> permutation(points.size());
    iota(permutation.begin(), permutation.end(), 0);
    shuffle(permutation.begin(), permutation.end(), rng);
    sort(permutation.begin(), permutation.end(), [&](int a, int b){return C{}(points[a],points[b]);});
    for (int i = 1; i < int(permutation.size()); i++)
        assert(!exact_less(exact[permutation[i]],exact[permutation[i-1]]));
    cout << "{\"kind\":\"core\",\"label\":\"" << label << "\",\"digits\":" << p
         << ",\"rounding_mode\":" << mode << ",\"coordinate_exponent_min\":" << lo
         << ",\"coordinate_exponent_max\":" << hi << ",\"exact_pairs\":" << pairs
         << ",\"grid_triples\":" << grid.size()*grid.size()*grid.size()
         << ",\"random_triples\":100000,\"sorted_points\":" << points.size()
         << ",\"passed\":true}\n";
}
int main(int argc, char **argv)
{
    using R = RealPlane::R;
    if (argc > 1 && string(argv[1]) == "--metadata")
    {
        cout << "{\"radix\":" << numeric_limits<R>::radix
             << ",\"digits\":" << numeric_limits<R>::digits
             << ",\"min_exponent\":" << numeric_limits<R>::min_exponent
             << ",\"max_exponent\":" << numeric_limits<R>::max_exponent
             << ",\"rounding_mode\":" << fegetround() << "}\n";
        return 0;
    }
    if (argc > 1 && string(argv[1]) == "--decode")
    {
        // Recover actual parsed values independently of frexp/product normalization.
        int n;
        if (!(cin >> n) || n < 0 || n > 200000) return 1;
        for (int i = 0; i < n; i++)
        {
            R x, y;
            if (!(cin >> x >> y) || !isfinite(x) || !isfinite(y)) return 1;
            printf("%.*La %.*La\n", (numeric_limits<R>::digits + 3) / 4, x,
                   (numeric_limits<R>::digits + 3) / 4, y);
        }
        return 0;
    }
    if (argc > 1 && string(argv[1]) == "--invalid")
    {
        assert(argc == 4);
        R x = string(argv[2]) == "nan" ? numeric_limits<R>::quiet_NaN()
                                      : numeric_limits<R>::infinity();
        RealPlane::Point a{0, 0}, b{0, 0};
        int coordinate = stoi(argv[3]);
        assert(0 <= coordinate && coordinate < 4);
        if (coordinate == 0) a.x = x;
        if (coordinate == 1) a.y = x;
        if (coordinate == 2) b.x = x;
        if (coordinate == 3) b.y = x;
        return RealPolarLess{}(a, b);
    }
    assert(argc == 1);
    int original_rounding = fegetround();
    for (int mode : {FE_TONEAREST, FE_UPWARD, FE_DOWNWARD, FE_TOWARDZERO})
    {
        assert(fesetround(mode) == 0);
        run<RealPolarLess>("actual-long-double", mode);
#ifdef REAL_POLAR_TYPE_PROBES
        run<test_float::RealPolarLess>("unchanged-body-float", mode);
        run<test_double::RealPolarLess>("unchanged-body-double", mode);
#endif
    }
    assert(fesetround(original_rounding) == 0);
}
