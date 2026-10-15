#include "../src/compact/stirling.hpp"
#include <cassert>
#include <iostream>
using Z = ModInt<998244353>;
int main()
{
    const int n = 150;
    vector<vector<Z>> c(n + 1, vector<Z>(n + 1));
    auto s = c;
    c[0][0] = s[0][0] = 1;
    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= i; j++)
        {
            c[i][j] = c[i - 1][j - 1] + c[i - 1][j] * (i - 1);
            s[i][j] = s[i - 1][j - 1] + s[i - 1][j] * j;
        }
    long long checked = 0;
    for (int k = 0; k <= n + 2; k++)
    {
        auto first = stirling_first_column(n, k);
        auto second = stirling_second_column(n, k);
        for (int i = 0; i <= n; i++)
        {
            assert(first[i].v == (k <= n ? c[i][k].v : 0));
            assert(second[i].v == (k <= n ? s[i][k].v : 0));
            checked += 2;
        }
    }
    for (int i = 0; i <= n; i++)
    {
        auto first = stirling_first_row(i);
        auto second = stirling_second_row(i, i);
        for (int j = 0; j <= i; j++)
        {
            assert(first[j].v == c[i][j].v);
            assert(second[j].v == s[i][j].v);
            checked += 2;
        }
    }
    for (int i = 0; i <= n; i++)
        for (int j = 0; j <= i; j++)
        {
            Z value = 0;
            for (int k = j; k <= i; k++)
            {
                Z term = s[i][k] * c[k][j];
                if ((k - j) % 2)
                    term = Z(0) - term;
                value += term;
            }
            assert(value.v == (i == j));
        }
    for (int size : {0, 1, 2, 7, 31, 32, 33, 500000})
    {
        auto a = stirling_first_column(size, 0);
        auto b = stirling_second_column(size, 0);
        assert(a[0].v == 1 && b[0].v == 1);
        a = stirling_first_column(size, 1);
        b = stirling_second_column(size, 1);
        Z fact = 1;
        for (int i = 1; i <= size; i++)
        {
            assert(a[i].v == fact.v && b[i].v == 1);
            fact *= i;
        }
        a = stirling_first_column(size, size);
        b = stirling_second_column(size, size);
        assert(a[size].v == 1 && b[size].v == 1);
    }
    cout << checked << " row/column coefficients; inversion; 500000 boundary PASS\n";
}
