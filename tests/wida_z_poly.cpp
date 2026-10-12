#include <bits/stdc++.h>
#include <cassert>
using namespace std;
namespace source
{
#include "fixtures/wida_poly_variants/12B.cpp"
}
#include "../src/compact/fps_power.hpp"
#include "../src/compact/fps_sqrt.hpp"
#include "../src/compact/multipoint_evaluation.hpp"
using V = vector<long long>;
constexpr long long P = 998244353;
long long checks = 0;
void check(bool ok)
{
    if (!ok)
        throw runtime_error("mismatch at " + to_string(checks));
    checks++;
}
long long power(long long a, long long b)
{
    long long r = 1;
    while (b)
    {
        if (b & 1)
            r = r * a % P;
        a = a * a % P;
        b >>= 1;
    }
    return r;
}
V multiply(const V &a, const V &b, int n)
{
    V c(n);
    for (int i = 0; i < (int)a.size(); i++)
        for (int j = 0; j < (int)b.size() && i + j < n; j++)
            c[i + j] = (c[i + j] + a[i] * b[j]) % P;
    return c;
}
V inverse(const V &a, int n)
{
    V b(n);
    b[0] = power(a[0], P - 2);
    for (int i = 1; i < n; i++)
    {
        long long s = 0;
        for (int j = 1; j <= i && j < (int)a.size(); j++)
            s = (s + a[j] * b[i - j]) % P;
        b[i] = (P - s) * b[0] % P;
    }
    return b;
}
V logarithm(const V &a, int n)
{
    V d;
    for (int i = 1; i < (int)a.size(); i++)
        d.push_back(a[i] * i % P);
    auto p = multiply(d, inverse(a, n), n - 1);
    V r(n);
    for (int i = 1; i < n; i++)
        r[i] = p[i - 1] * power(i, P - 2) % P;
    return r;
}
V exponential(const V &a, int n)
{
    V b(n);
    b[0] = 1;
    for (int i = 1; i < n; i++)
    {
        for (int j = 1; j <= i && j < (int)a.size(); j++)
            b[i] = (b[i] + a[j] * j % P * b[i - j]) % P;
        b[i] = b[i] * power(i, P - 2) % P;
    }
    return b;
}
source::Poly original(const V &a)
{
    vector<source::Z> b;
    for (auto x : a)
        b.emplace_back(x);
    return source::Poly(b);
}
FpsInverse::Poly current(const V &a)
{
    return FpsInverse::Poly(a.begin(), a.end());
}
void same(const source::Poly &a, const V &b)
{
    check(a.size() <= (int)b.size());
    for (int i = 0; i < (int)b.size(); i++)
        check(a[i].val() == b[i]);
}
void same(const FpsInverse::Poly &a, const V &b)
{
    check(a.size() == b.size());
    for (int i = 0; i < (int)b.size(); i++)
        check(a[i].v == b[i]);
}
int main(int argc, char **argv)
{
    string task = argc > 1 ? argv[1] : "small";
    if (task == "singleton")
    {
        vector<source::Z> a{1};
        source::dft(a);
        return 0;
    }
    if (task == "counterexamples")
    {
        same(original({0}).pow(0, 4), {0, 0, 0, 0});
        same(FpsPower::power(current({0}), "0", 4), {1, 0, 0, 0});
        same(original({4}).sqrt(1), {1});
        auto r = FpsSqrt::sqrt(current({4}), 1);
        check(r.has_value());
        same(*r, {2});
        check(source::Z(INT_MAX).val() != INT_MAX % P);
        check(source::Z((long long)INT_MAX).val() == INT_MAX % P);
        cout << checks << " documented source counterexample checks PASS\n";
        return 0;
    }
    if (task == "large")
    {
        int n = 1 << 15;
        V geometric(n, 1), denominator{1, P - 1};
        same(original(denominator).inv(n), geometric);
        same(FpsInverse::inverse(current(denominator), n), geometric);
        V log(n), argument(n), exp(n);
        exp[0] = 1;
        for (int i = 1; i < n; i++)
        {
            log[i] = (P - power(i, P - 2)) % P;
            exp[i] = exp[i - 1] * power(i, P - 2) % P;
        }
        argument[1] = 1;
        same(original(denominator).log(n), log);
        same(FpsFunctions::log(current(denominator), n), log);
        same(original(argument).exp(n), exp);
        same(FpsFunctions::exp(current(argument), n), exp);
        V square(n), square_root(n, 1);
        for (int i = 0; i < n; i++)
            square[i] = i + 1;
        same(original(square).sqrt(n), square_root);
        auto r = FpsSqrt::sqrt(current(square), n);
        check(r.has_value());
        same(*r, square_root);
        V points(2048), polynomial(2049), values(2048);
        polynomial[0] = 3;
        polynomial[2048] = 1;
        for (int i = 0; i < 2048; i++)
        {
            points[i] = i;
            values[i] = (power(i, 2048) + 3) % P;
        }
        same(source::Poly(original(polynomial).eval(original(points).a)), values);
        same(MultipointEvaluation(current(points)).evaluate(current(polynomial)), values);
        cout << checks << " analytic large-series/evaluation checks PASS\n";
        return 0;
    }
    mt19937 rng(38664055);
    for (int n : {0, 1, 2, 3, 7, 16, 31, 64, 127, 128, 129, 257})
    {
        V a(n), b(n + 1);
        for (auto &x : a)
            x = rng() % P;
        for (auto &x : b)
            x = rng() % P;
        auto f = original(a), g = original(b);
        V plus(n + 1), minus(n + 1), negative(n), scaled(n);
        for (int i = 0; i <= n; i++)
        {
            plus[i] = ((i < n ? a[i] : 0) + b[i]) % P;
            minus[i] = ((i < n ? a[i] : 0) - b[i] + P) % P;
            if (i < n)
            {
                negative[i] = (P - a[i]) % P;
                scaled[i] = a[i] * 7 % P;
            }
        }
        same(f + g, plus);
        same(f - g, minus);
        same(-f, negative);
        same(f * source::Z(7), scaled);
        same(source::Z(7) * f, scaled);
        auto copy = f;
        copy += g;
        same(copy, plus);
        copy = f;
        copy -= g;
        same(copy, minus);
        copy = f;
        copy *= source::Z(7);
        same(copy, scaled);
        V product = n ? multiply(a, b, 2 * n) : V{};
        same(f * g, product);
        copy = f;
        copy *= g;
        same(copy, product);
        same(FpsInverse::multiply(current(a), current(b)), product);
        for (int k : {0, 1, n, n + 3})
        {
            V shifted(k);
            shifted.insert(shifted.end(), a.begin(), a.end());
            same(f.mulxk(k), shifted);
            same(f.modxk(k), V(a.begin(), a.begin() + min(k, n)));
            same(f.divxk(k), V(a.begin() + min(k, n), a.end()));
        }
        V derivative(max(0, n - 1)), integral(n + 1);
        for (int i = 1; i < n; i++)
            derivative[i - 1] = a[i] * i % P;
        for (int i = 0; i < n; i++)
            integral[i + 1] = a[i] * power(i + 1, P - 2) % P;
        same(f.deriv(), derivative);
        same(f.integr(), integral);
        same(FpsFunctions::derivative(current(a)), derivative);
        same(FpsFunctions::integral(current(a)), integral);
        V transpose(n);
        for (int i = 0; i < n; i++)
            for (int j = 0; i + j < n; j++)
                transpose[i] = (transpose[i] + a[i + j] * b[j]) % P;
        same(f.mulT(g), transpose);
        auto reversed = current(b);
        reverse(reversed.begin(), reversed.end());
        auto transposed = FpsInverse::multiply(current(a), reversed);
        if (!transposed.empty())
            transposed.erase(transposed.begin(), transposed.begin() + b.size() - 1);
        same(transposed, transpose);
        same(f.mulT(source::Poly()), {});
        for (int count : {0, 1, 5, n + 3})
        {
            V points(count), truth(count);
            for (int j = 0; j < count; j++)
            {
                points[j] = j % 4 == 0 ? 0 : rng() % 7;
                for (int i = n - 1; i >= 0; i--)
                    truth[j] = (truth[j] * points[j] + a[i]) % P;
            }
            auto values = f.eval(original(points).a);
            same(source::Poly(values), truth);
            same(MultipointEvaluation(current(points)).evaluate(current(a)), truth);
        }
        if (!n)
            continue;
        a[0] = 1;
        f = original(a);
        same(f.inv(n), inverse(a, n));
        same(FpsInverse::inverse(current(a), n), inverse(a, n));
        same(f.log(n), logarithm(a, n));
        same(FpsFunctions::log(current(a), n), logarithm(a, n));
        auto square = multiply(a, a, n);
        same(original(square).sqrt(n), a);
        auto root = FpsSqrt::sqrt(current(square), n);
        check(root.has_value());
        same(*root, a);
        a[0] = 0;
        same(original(a).exp(n), exponential(a, n));
        same(FpsFunctions::exp(current(a), n), exponential(a, n));
        for (int k : {1, 2, 3, 7})
        {
            V expected(n);
            expected[0] = 1;
            for (int j = 0; j < k; j++)
                expected = multiply(expected, a, n);
            same(original(a).pow(k, n), expected);
            same(FpsPower::power(current(a), to_string(k), n), expected);
        }
    }
    for (int t = 0; t < 250; t++)
    {
        int len = 1 + rng() % 40, n = 1 + rng() % 65;
        V a(len);
        for (auto &x : a)
            x = rng() % P;
        a[0] = 1 + rng() % (P - 1);
        same(original(a).inv(n), inverse(a, n));
        same(FpsInverse::inverse(current(a), n), inverse(a, n));
        int k = rng() % 8;
        V expected(n);
        expected[0] = 1;
        for (int j = 0; j < k; j++)
            expected = multiply(expected, a, n);
        same(original(a).pow(k, n), expected);
        same(FpsPower::power(current(a), to_string(k), n), expected);
        a[0] = 1;
        same(original(a).log(n), logarithm(a, n));
        same(FpsFunctions::log(current(a), n), logarithm(a, n));
        auto square = multiply(a, a, n);
        auto truth = a;
        truth.resize(n);
        same(original(square).sqrt(n), truth);
        same(*FpsSqrt::sqrt(current(square), n), truth);
        a[0] = 0;
        same(original(a).exp(n), exponential(a, n));
        same(FpsFunctions::exp(current(a), n), exponential(a, n));
    }
    cout << checks << " independent Poly interface checks PASS\n";
}
