#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <cmath>
#include <utility>
#include <vector>
using namespace std;

// BEGIN GaussReal
struct GaussReal
{
    using R = long double;
    using Matrix = vector<vector<R>>;

    struct Solution
    {
        bool consistent;
        int rank;
        vector<R> particular;
        Matrix kernel;
    };

    // Numerical classification after coefficient-row scaling, not exact rank.
    static Solution solve(Matrix a, int n, R eps)
    {
        assert(0 <= n && n < INT_MAX && a.size() <= (size_t)INT_MAX);
        assert(isfinite(eps) && 0 < eps && eps < 1);
        int m = a.size(), row = 0;
        vector<int> where(n, -1);
        for (auto &v : a)
        {
            assert(v.size() == (size_t)n + 1);
            R s = 0;
            for (int j = 0; j <= n; j++)
            {
                assert(isfinite(v[j]));
                if (j < n) s = max(s, abs(v[j]));
            }
            if (s > 0)
                for (R &x : v)
                {
                    x /= s;
                    assert(isfinite(x));
                }
        }
        for (int col = 0; col < n && row < m; col++)
        {
            int p = row;
            for (int i = row + 1; i < m; i++)
                if (abs(a[i][col]) > abs(a[p][col])) p = i;
            if (abs(a[p][col]) <= eps)
            {
                for (int i = row; i < m; i++) a[i][col] = 0;
                continue;
            }
            swap(a[p], a[row]);
            R pivot = a[row][col];
            for (int j = col + 1; j <= n; j++)
            {
                a[row][j] /= pivot;
                assert(isfinite(a[row][j]));
            }
            a[row][col] = 1;
            for (int i = 0; i < m; i++)
                if (i != row && a[i][col] != 0)
                {
                    R f = a[i][col];
                    for (int j = col + 1; j <= n; j++)
                    {
                        a[i][j] -= f * a[row][j];
                        assert(isfinite(a[i][j]));
                    }
                    a[i][col] = 0;
                }
            where[col] = row++;
        }
        for (int i = row; i < m; i++)
            if (abs(a[i][n]) > eps) return {false, row, {}, {}};
        Solution ans{true, row, vector<R>(n), {}};
        for (int j = 0; j < n; j++)
            if (where[j] != -1) ans.particular[j] = a[where[j]][n];
        for (int j = 0; j < n; j++)
            if (where[j] == -1)
            {
                vector<R> v(n);
                v[j] = 1;
                for (int k = 0; k < n; k++)
                    if (where[k] != -1) v[k] = -a[where[k]][j];
                ans.kernel.push_back(v);
            }
        return ans;
    }
};

// END GaussReal
