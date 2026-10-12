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
using Z = FpsInverse::Z;
using Poly = FpsInverse::Poly;
constexpr int P = 998244353;
int main(int argc, char **argv)
{
    string operation = argv[1], implementation = argv[2];
    int n = stoi(argv[3]);
    bool old = implementation == "original";
    Poly a(n), truth(n), result;
    vector<Z> inv(n + 1);
    inv[1] = 1;
    for (int i = 2; i <= n; i++)
        inv[i] = Z(0) - Z(P / i) * inv[P % i];
    if (operation == "inverse" || operation == "log")
    {
        a[0] = 1;
        a[1] = P - 1;
        if (operation == "inverse")
            fill(truth.begin(), truth.end(), Z(1));
        else
            for (int i = 1; i < n; i++)
                truth[i] = Z(0) - inv[i];
    }
    else if (operation == "exp")
    {
        a[1] = 1;
        truth[0] = 1;
        for (int i = 1; i < n; i++)
            truth[i] = truth[i - 1] * inv[i];
    }
    else if (operation == "sqrt")
    {
        for (int i = 0; i < n; i++)
            a[i] = i + 1;
        fill(truth.begin(), truth.end(), Z(1));
    }
    else if (operation == "eval")
    {
        a[0] = 3;
        a[n - 1] = 1;
        for (int i = 0; i < n; i++)
            truth[i] = Z(i).pow(n - 1) + Z(3);
    }
    else
        throw runtime_error("unknown operation");
    source::Poly f(n);
    for (int i = 0; i < n; i++)
        f[i] = a[i].v;
    auto start = chrono::steady_clock::now();
    if (old)
    {
        source::Poly r;
        if (operation == "inverse")
            r = f.inv(n);
        if (operation == "log")
            r = f.log(n);
        if (operation == "exp")
            r = f.exp(n);
        if (operation == "sqrt")
            r = f.sqrt(n);
        if (operation == "eval")
        {
            vector<source::Z> points(n);
            for (int i = 0; i < n; i++)
                points[i] = i;
            r = f.eval(points);
        }
        for (int i = 0; i < n; i++)
            result.push_back(r[i].val());
    }
    else
    {
        if (operation == "inverse")
            result = FpsInverse::inverse(a, n);
        if (operation == "log")
            result = FpsFunctions::log(a, n);
        if (operation == "exp")
            result = FpsFunctions::exp(a, n);
        if (operation == "sqrt")
            result = *FpsSqrt::sqrt(a, n);
        if (operation == "eval")
        {
            Poly points(n);
            for (int i = 0; i < n; i++)
                points[i] = i;
            result = MultipointEvaluation(points).evaluate(a);
        }
    }
    double seconds = chrono::duration<double>(chrono::steady_clock::now() - start).count();
    if (result.size() != truth.size())
        throw runtime_error("wrong size");
    unsigned long long hash = 1469598103934665603ULL;
    for (int i = 0; i < n; i++)
    {
        if (result[i].v != truth[i].v)
            throw runtime_error("coefficient mismatch at " + to_string(i));
        hash = (hash ^ (unsigned)result[i].v) * 1099511628211ULL;
    }
    cout << n << ' ' << hash << ' ' << setprecision(12) << seconds << " PASS\n";
}
