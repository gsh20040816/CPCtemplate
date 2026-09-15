#pragma once
#include "number_theory.hpp"
#include <optional>

// BEGIN matrix_inverse
template <int mod>
optional<vector<vector<ModInt<mod>>>> matrix_inverse(vector<vector<ModInt<mod>>> a)
{
    using Z = ModInt<mod>;
    int n = a.size();
    vector<vector<Z>> b(n, vector<Z>(n));
    for (int i = 0; i < n; i++)
    {
        assert((int)a[i].size() == n);
        b[i][i] = 1;
    }
    for (int i = 0; i < n; i++)
    {
        int p = i;
        while (p < n && !a[p][i].v) p++;
        if (p == n) return nullopt;
        swap(a[p], a[i]);
        swap(b[p], b[i]);
        Z inv = a[i][i].inv();
        for (int k = i; k < n; k++) a[i][k] = a[i][k] * inv;
        for (int k = 0; k < n; k++) b[i][k] = b[i][k] * inv;
        for (int j = 0; j < n; j++)
            if (j != i && a[j][i].v)
            {
                Z f = a[j][i];
                for (int k = i; k < n; k++) a[j][k] = a[j][k] - f * a[i][k];
                for (int k = 0; k < n; k++) b[j][k] = b[j][k] - f * b[i][k];
            }
    }
    return b;
}

// END matrix_inverse
