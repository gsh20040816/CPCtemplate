#include <bits/stdc++.h>
#include <cassert>
using namespace std;
namespace source
{
#include "fixtures/wida_poly_variants/12A.cpp"
}
#include "../src/compact/fps_functions.hpp"
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
    return source::Poly(vector<int>(a.begin(), a.end()));
}
V unpack(const source::Poly &a)
{
    return V(a.a.begin(), a.a.end());
}
FpsInverse::Poly current(const V &a)
{
    return FpsInverse::Poly(a.begin(), a.end());
}
V unpack(const FpsInverse::Poly &a)
{
    V b;
    for (auto x : a)
        b.push_back(x.v);
    return b;
}
void same(V got, V expected)
{
    while (!got.empty() && got.back() == 0)
        got.pop_back();
    while (!expected.empty() && expected.back() == 0)
        expected.pop_back();
    check(got == expected);
    checks += expected.size();
}
int main(int argc, char **argv)
{
    string task = argv[1];
    if (task == "source-constant" || task == "source-log" || task == "source-exp")
    {
        source::Poly result;
        if (task == "source-constant")
            result = source::Poly(2) * source::Poly(3);
        if (task == "source-log")
            result = source::Poly(1).log(8);
        if (task == "source-exp")
            result = original({0, 1}).exp(8);
        cout << result.size() << '\n';
        return 0;
    }
    bool old = task == "source" || task == "source-safe";
    mt19937 rng(119653035);
    for (int length : {0, 1, 2, 3, 17, 64, 129, 257})
    {
        V a(length), b(length + 3);
        for (auto &x : a)
            x = rng() % P;
        for (auto &x : b)
            x = rng() % P;
        if (!a.empty())
            a.back() = 0;
        auto f = original(a), g = original(b);
        if (old)
        {
            check(f[-1] == 0 && f[length + 5] == 0);
            V normalized = a;
            while (!normalized.empty() && normalized.back() == 0)
                normalized.pop_back();
            check(unpack(f) == normalized);
            for (int k : {0, 1, length, length + 3})
            {
                V shifted(k);
                shifted.insert(shifted.end(), a.begin(), a.end());
                same(unpack(f.mulxk(k)), shifted);
                same(unpack(f.modxk(k)), V(a.begin(), a.begin() + min(k, length)));
                same(unpack(f.divxk(k)), V(a.begin() + min(k, length), a.end()));
            }
            V sum(b.size()), difference(b.size());
            for (int i = 0; i < (int)b.size(); i++)
            {
                sum[i] = ((i < length ? a[i] : 0) + b[i]) % P;
                difference[i] = ((i < length ? a[i] : 0) - b[i] + P) % P;
            }
            same(unpack(f + g), sum);
            same(unpack(f - g), difference);
            auto c = f;
            c += g;
            same(unpack(c), sum);
            c = f;
            c -= g;
            same(unpack(c), difference);
            if (task != "source-safe")
            {
                c = f;
                c *= g;
                same(unpack(c), multiply(a, b, a.size() + b.size()));
            }
        }
        if (task != "source-safe")
            same(old ? unpack(f * g) : unpack(FpsInverse::multiply(current(a), current(b))), multiply(a, b, a.size() + b.size()));
        V derivative(max(0, length - 1)), integral(length + 1);
        for (int i = 1; i < length; i++)
            derivative[i - 1] = a[i] * i % P;
        for (int i = 0; i < length; i++)
            integral[i + 1] = a[i] * power(i + 1, P - 2) % P;
        same(old ? unpack(f.deriv()) : unpack(FpsFunctions::derivative(current(a))), derivative);
        same(old ? unpack(f.integr()) : unpack(FpsFunctions::integral(current(a))), integral);
        if (task == "source-safe")
            continue;
        V transpose(a.size());
        for (int i = 0; i < (int)a.size(); i++)
            for (int j = 0; j < (int)b.size() && i + j < (int)a.size(); j++)
                transpose[i] = (transpose[i] + a[i + j] * b[j]) % P;
        if (old)
        {
            same(unpack(f.mulT(g)), transpose);
            same(unpack(f.mulT(source::Poly())), {});
        }
        for (int count : {0, 1, 7, length + 2})
        {
            vector<int> points(count);
            V truth(count);
            for (int i = 0; i < count; i++)
            {
                points[i] = i % 5;
                for (int j = length - 1; j >= 0; j--)
                    truth[i] = (truth[i] * points[i] + a[j]) % P;
            }
            if (old)
            {
                auto answer = f.eval(points);
                check(answer.size() == points.size());
                same(V(answer.begin(), answer.end()), truth);
            }
            else
                same(unpack(MultipointEvaluation(current(V(points.begin(), points.end()))).evaluate(current(a))), truth);
        }
    }
    if (task == "source-safe")
    {
        V a(129, 1), b(257, 1);
        same(unpack(original(a) * original(b)), multiply(a, b, a.size() + b.size()));
        cout << checks << " defined-domain source arithmetic checks PASS\n";
        return 0;
    }
    for (int trial = 0; trial < 200; trial++)
    {
        int length = 1 + rng() % 45, n = 1 + rng() % 70;
        V a(length);
        for (auto &x : a)
            x = rng() % P;
        a[0] = 1 + rng() % (P - 1);
        same(old ? unpack(original(a).inv(n)) : unpack(FpsInverse::inverse(current(a), n)), inverse(a, n));
        a[0] = 1;
        same(old ? unpack(original(a).log(n)) : unpack(FpsFunctions::log(current(a), n)), logarithm(a, n));
        auto square = multiply(a, a, n);
        V expected = a;
        expected.resize(n);
        same(old ? unpack(original(square).sqrt(n)) : unpack(*FpsSqrt::sqrt(current(square), n)), expected);
        a[0] = 0;
        same(old ? unpack(original(a).exp(n)) : unpack(FpsFunctions::exp(current(a), n)), exponential(a, n));
    }
    cout << checks << " independent raw polynomial checks PASS\n";
}
