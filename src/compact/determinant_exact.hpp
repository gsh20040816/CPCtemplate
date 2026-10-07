#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

// BEGIN determinant_exact
template<class Z>
Z determinant_exact(vector<vector<Z>> a)
{
    int n = a.size();
    for (const auto &row : a)
        assert((int)row.size() == n);
    if (!n)
        return Z(1);
    Z prev = 1;
    int sign = 1;
    for (int k = 0; k + 1 < n; k++)
    {
        int p = k;
        while (p < n && a[p][k] == 0)
            p++;
        if (p == n)
            return Z(0);
        if (p != k)
        {
            swap(a[p], a[k]);
            sign = -sign;
        }
        Z pivot = a[k][k];
        for (int i = k + 1; i < n; i++)
        {
            for (int j = k + 1; j < n; j++)
            {
                Z value = a[i][j] * pivot - a[i][k] * a[k][j];
                a[i][j] = value / prev;
            }
            a[i][k] = 0;
        }
        prev = pivot;
    }
    return sign * a[n - 1][n - 1];
}
// END determinant_exact
