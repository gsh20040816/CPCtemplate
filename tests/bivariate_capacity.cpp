#include <bits/stdc++.h>
#include <cassert>
namespace original
{
#include "fixtures/wida_poly_variants/12A.cpp"
}
#include "../src/compact/bivariate_inverse.hpp"
using namespace std;
int main(int argc, char **argv)
{
    string mode = argv[1];
    if (mode == "constant")
    {
        auto c = original::Poly(2) * original::Poly(3);
        cout << c[0] << '\n';
        return c[0] != 6;
    }
    constexpr int n = 1024, p = 998244353;
    vector<vector<int>> expected(n, vector<int>(n));
    expected[0][0] = 1;
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
        {
            if (i)
                expected[i][j] = expected[i - 1][j];
            if (j)
                expected[i][j] = (expected[i][j] + expected[i][j - 1]) % p;
        }
    auto start = chrono::steady_clock::now();
    if (mode == "original")
    {
        vector<vector<int>> a(n, vector<int>(n));
        a[0][0] = 1;
        a[0][1] = a[1][0] = p - 1;
        auto b = original::inv(a);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                if (b[i][j] != expected[i][j])
                    return 2;
    }
    else
    {
        auto b = BivariateInverse::inverse({{1, p - 1}, {p - 1}}, n, n);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                if (b[i][j].v != expected[i][j])
                    return 3;
    }
    cout << chrono::duration<double>(chrono::steady_clock::now() - start).count();
    cout << " seconds; 1048576 Pascal recurrence coefficients PASS\n";
}
