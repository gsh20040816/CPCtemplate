#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN matrix_inverse_mod2
optional<vector<string>> matrix_inverse_mod2(const vector<string> &a)
{
    int n = a.size(), words = (2LL * n + 63) / 64;
    vector<vector<uint64_t>> b(n, vector<uint64_t>(words));
    for (int i = 0; i < n; i++)
    {
        assert((int)a[i].size() == n);
        for (int j = 0; j < n; j++)
        {
            assert(a[i][j] == '0' || a[i][j] == '1');
            if (a[i][j] == '1') b[i][j / 64] |= 1ULL << (j % 64);
        }
        b[i][(n + i) / 64] |= 1ULL << ((n + i) % 64);
    }
    for (int i = 0; i < n; i++)
    {
        int p = i;
        uint64_t mask = 1ULL << (i % 64);
        while (p < n && !(b[p][i / 64] & mask)) p++;
        if (p == n) return nullopt;
        swap(b[p], b[i]);
        for (int j = 0; j < n; j++)
            if (j != i && (b[j][i / 64] & mask))
                for (int k = i / 64; k < words; k++) b[j][k] ^= b[i][k];
    }
    vector<string> ans(n, string(n, '0'));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            if ((b[i][(n + j) / 64] >> ((n + j) % 64)) & 1) ans[i][j] = '1';
    return ans;
}

// END matrix_inverse_mod2
