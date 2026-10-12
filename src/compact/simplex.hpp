#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN Simplex
struct Simplex
{
    using Real = long double;
    static constexpr Real eps = 1e-12L;
    enum Status { optimal, infeasible, unbounded };
    struct Result
    {
        Status status;
        Real value;
        vector<Real> x;
    };
    int n, m;
    vector<int> basic, nonbasic;
    vector<vector<Real>> d;

    Simplex(const vector<vector<Real>> &a, const vector<Real> &b,
            const vector<Real> &c) : n(c.size()), m(b.size()),
            basic(m), nonbasic(n + 1), d(m + 2, vector<Real>(n + 2))
    {
        assert((int)a.size() == m);
        for (int i = 0; i < m; i++)
        {
            assert((int)a[i].size() == n);
            for (int j = 0; j < n; j++) d[i][j] = a[i][j];
            basic[i] = n + i;
            d[i][n] = -1;
            d[i][n + 1] = b[i];
        }
        iota(nonbasic.begin(), nonbasic.end(), 0);
        nonbasic[n] = n + m;
        for (int j = 0; j < n; j++) d[m][j] = -c[j];
        d[m + 1][n] = 1;
    }
    void pivot(int r, int s)
    {
        Real inv = 1 / d[r][s];
        for (int i = 0; i < m + 2; i++)
        {
            if (i == r) continue;
            Real scale = d[i][s] * inv;
            for (int j = 0; j < n + 2; j++)
                if (j != s) d[i][j] -= scale * d[r][j];
        }
        for (int j = 0; j < n + 2; j++)
            if (j != s) d[r][j] *= inv;
        for (int i = 0; i < m + 2; i++)
            if (i != r) d[i][s] *= -inv;
        d[r][s] = inv;
        swap(basic[r], nonbasic[s]);
    }
    bool improve(int objective)
    {
        while (true)
        {
            int s = -1;
            for (int j = 0; j <= n; j++)
            {
                if (nonbasic[j] == n + m) continue;
                if (d[objective][j] >= -eps) continue;
                if (s == -1 || nonbasic[j] < nonbasic[s]) s = j;
            }
            if (s == -1) return true;
            int r = -1;
            for (int i = 0; i < m; i++)
            {
                if (d[i][s] <= eps) continue;
                if (r == -1)
                {
                    r = i;
                    continue;
                }
                Real x = d[i][n + 1] / d[i][s];
                Real y = d[r][n + 1] / d[r][s];
                if (x < y - eps || (abs(x - y) <= eps && basic[i] < basic[r]))
                    r = i;
            }
            if (r == -1) return false;
            pivot(r, s);
        }
    }
    Result solve()
    {
        int r = -1;
        for (int i = 0; i < m; i++)
            if (r == -1 || d[i][n + 1] < d[r][n + 1]) r = i;
        if (r != -1 && d[r][n + 1] < -eps)
        {
            pivot(r, n);
            improve(m + 1);
            if (d[m + 1][n + 1] < -eps) return {infeasible, 0, {}};
            for (int i = 0; i < m; i++)
            {
                if (basic[i] != n + m) continue;
                int s = -1;
                for (int j = 0; j <= n; j++)
                    if (abs(d[i][j]) > eps &&
                        (s == -1 || nonbasic[j] < nonbasic[s])) s = j;
                if (s != -1) pivot(i, s);
            }
        }
        if (!improve(m)) return {unbounded, 0, {}};
        vector<Real> x(n);
        for (int i = 0; i < m; i++)
            if (basic[i] < n) x[basic[i]] = d[i][n + 1];
        return {optimal, d[m][n + 1], x};
    }
};
// END Simplex
