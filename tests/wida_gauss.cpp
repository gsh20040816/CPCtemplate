#include <bits/stdc++.h>
#include <cassert>
using namespace std;
namespace source
{
int P = 998244353;
int power(int a, int n)
{
    int r = 1;
    while (n)
    {
        if (n & 1)
            r = 1LL * r * a % P;
        a = 1LL * a * a % P;
        n >>= 1;
    }
    return r;
}
#include "fixtures/wida_gauss/gauss.cpp"
}
#include "../src/compact/gauss_mod.hpp"
#include "../src/compact/gauss_real.hpp"
#include "../src/compact/polynomial_division.hpp"
long long checks = 0;
void check(bool ok)
{
    if (!ok)
        throw runtime_error("mismatch at " + to_string(checks));
    checks++;
}
int power(int a, int n)
{
    int r = 1;
    while (n--)
        r *= a;
    return r;
}
template<int p> void exhaustive(int limit)
{
    using G = GaussMod<p>;
    source::P = p;
    for (int n = 0; n <= limit; n++)
        for (int m = 0; m <= limit; m++)
        {
            int total = power(p, m * (n + 1));
            for (int code = 0; code < total; code++)
            {
                typename G::Matrix a(m, vector<typename G::Z>(n + 1));
                int value = code;
                for (auto &row : a)
                    for (auto &x : row)
                    {
                        x = value % p;
                        value /= p;
                    }
                set<vector<int>> solutions;
                int kernel_count = 0;
                for (int assignment = 0; assignment < power(p, n); assignment++)
                {
                    vector<int> x(n);
                    int v = assignment;
                    for (auto &y : x)
                    {
                        y = v % p;
                        v /= p;
                    }
                    bool solves = true, homogeneous = true;
                    for (const auto &row : a)
                    {
                        int sum = 0;
                        for (int j = 0; j < n; j++)
                            sum = (sum + row[j].v * x[j]) % p;
                        solves &= sum == row[n].v;
                        homogeneous &= sum == 0;
                    }
                    if (solves)
                        solutions.insert(x);
                    kernel_count += homogeneous;
                }
                int nullity = 0;
                while (power(p, nullity) < kernel_count)
                    nullity++;
                auto answer = G::solve(a, n);
                check(answer.rank == n - nullity);
                check(answer.consistent == !solutions.empty());
                if (answer.consistent)
                {
                    check(answer.kernel.size() == (size_t)nullity);
                    set<vector<int>> generated;
                    for (int coefficients = 0; coefficients < kernel_count; coefficients++)
                    {
                        vector<int> x(n);
                        for (int i = 0; i < n; i++)
                            x[i] = answer.particular[i].v;
                        int v = coefficients;
                        for (const auto &basis : answer.kernel)
                        {
                            int c = v % p;
                            v /= p;
                            for (int i = 0; i < n; i++)
                                x[i] = (x[i] + c * basis[i].v) % p;
                        }
                        generated.insert(x);
                    }
                    check(generated == solutions);
                    if (m == n && nullity == 0)
                    {
                        vector<vector<int>> matrix(n, vector<int>(n));
                        vector<int> b(n);
                        for (int i = 0; i < n; i++)
                        {
                            for (int j = 0; j < n; j++)
                                matrix[i][j] = a[i][j].v;
                            b[i] = a[i][n].v;
                        }
                        check(source::gauss(matrix, b) == *solutions.begin());
                    }
                }
                else
                    check(answer.particular.empty() && answer.kernel.empty());
            }
        }
}
int main(int argc, char **argv)
{
    string task = argc > 1 ? argv[1] : "normal";
    if (task == "singular")
    {
        auto answer = source::gauss(vector<vector<int>>{{0}}, vector<int>{0});
        cout << answer[0] << '\n';
        return 0;
    }
    exhaustive<2>(3);
    exhaustive<3>(2);
    auto floating = source::gauss(vector<vector<double>>{{0, 1}, {1, 0}}, vector<double>{2, 3});
    check(!isfinite(floating[0]) || !isfinite(floating[1]));
    auto corrected = GaussReal::solve({{0, 1, 2}, {1, 0, 3}}, 2, 1e-12L);
    check(corrected.consistent && corrected.rank == 2);
    check(abs(corrected.particular[0] - 3) < 1e-12L && abs(corrected.particular[1] - 2) < 1e-12L);
    mt19937 rng(91334513);
    for (int trial = 0; trial < 150; trial++)
    {
        int n = 1 + rng() % 15;
        vector<double> truth(n), b(n);
        vector<vector<double>> a(n, vector<double>(n));
        GaussReal::Matrix augmented(n, vector<long double>(n + 1));
        for (auto &x : truth)
            x = int(rng() % 21) - 10;
        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < n; j++)
            {
                a[i][j] = i == j ? 4 * n : int(rng() % 5) - 2;
                augmented[i][j] = a[i][j];
                b[i] += a[i][j] * truth[j];
            }
            augmented[i][n] = b[i];
        }
        auto old = source::gauss(a, b);
        auto now = GaussReal::solve(augmented, n, 1e-12L);
        check(now.consistent && now.rank == n);
        for (int i = 0; i < n; i++)
        {
            check(abs(old[i] - truth[i]) < 1e-9);
            check(abs(now.particular[i] - truth[i]) < 1e-9L);
        }
    }
    source::P = 998244353;
    for (int trial = 0; trial < 250; trial++)
    {
        int n = 1 + rng() % 35, m = 1 + rng() % 35;
        vector<int> q(n), b(m), remainder(m - 1);
        for (auto *a : {&q, &b, &remainder})
            for (int &x : *a)
                x = rng() % source::P;
        b.back() = 1 + rng() % (source::P - 1);
        q.back() = 1 + rng() % (source::P - 1);
        vector<int> a(n + m - 1);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++)
                a[i + j] = (a[i + j] + 1LL * q[i] * b[j]) % source::P;
        check(source::operator*(q, b) == a);
        for (int i = 0; i < m - 1; i++)
            a[i] = (a[i] + remainder[i]) % source::P;
        check(source::operator%(a, b) == remainder);
        using F = PolynomialDivision;
        auto result = F::divide(F::Poly(a.begin(), a.end()), F::Poly(b.begin(), b.end()));
        check(result.first.size() == q.size());
        for (int i = 0; i < n; i++)
            check(result.first[i].v == q[i]);
        while (!remainder.empty() && !remainder.back())
            remainder.pop_back();
        check(result.second.size() == remainder.size());
        for (int i = 0; i < (int)remainder.size(); i++)
            check(result.second[i].v == remainder[i]);
    }
    cout << checks << " exhaustive solution-space and source-contract checks PASS\n";
}
