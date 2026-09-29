#pragma once
#include <algorithm>
#include <cassert>
#include <string>
#include <vector>
using namespace std;

struct GaussXor
{
    struct Solution
    {
        bool consistent;
        int rank;
        string particular;
        vector<string> kernel;
    };

    // m rows of n+1 characters: coefficients followed by the right-hand side.
    static Solution solve(const vector<string> &a, int n)
    {
        assert(n >= 0);
        int m = a.size(), w = n / 64 + 1, row = 0;
        vector<vector<unsigned long long>> b(m, vector<unsigned long long>(w));
        for (int i = 0; i < m; i++)
        {
            assert(a[i].size() == (size_t)n + 1);
            for (int j = 0; j <= n; j++)
            {
                assert(a[i][j] == '0' || a[i][j] == '1');
                if (a[i][j] == '1') b[i][j / 64] |= 1ULL << (j % 64);
            }
        }
        auto get = [&](int i, int j)
        {
            return b[i][j / 64] >> (j % 64) & 1;
        };
        vector<int> pos(n, -1);
        for (int col = 0; col < n && row < m; col++)
        {
            int p = row;
            while (p < m && !get(p, col)) p++;
            if (p == m) continue;
            swap(b[p], b[row]);
            for (int i = 0; i < m; i++)
                if (i != row && get(i, col))
                    for (int j = col / 64; j < w; j++) b[i][j] ^= b[row][j];
            pos[col] = row++;
        }
        for (int i = row; i < m; i++)
            if (get(i, n)) return {false, row, {}, {}};
        Solution ans{true, row, string(n, '0'), {}};
        for (int j = 0; j < n; j++)
            if (pos[j] != -1) ans.particular[j] += get(pos[j], n);
        for (int j = 0; j < n; j++)
            if (pos[j] == -1)
            {
                string v(n, '0');
                v[j] = '1';
                for (int k = 0; k < n; k++)
                    if (pos[k] != -1) v[k] += get(pos[k], j);
                ans.kernel.push_back(v);
            }
        return ans;
    }
};
