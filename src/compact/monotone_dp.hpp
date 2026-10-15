#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

// BEGIN monotone_dp_layer
template<class Cost>
vector<long long> monotone_dp_layer(const vector<long long> &prev, int first,
                                    Cost cost, vector<int> &opt)
{
    using ll = long long;
    constexpr ll inf = LLONG_MAX / 4;
    int n = int(prev.size()) - 1;
    assert(1 <= first && first <= n && prev[first - 1] != inf);
    vector<ll> cur(n + 1, inf);
    opt.assign(n + 1, -1);
    auto solve = [&](auto &&self, int l, int r, int lo, int hi) -> void
    {
        if (l > r) return;
        int mid = l + (r - l) / 2;
        for (int j = lo; j <= min(hi, mid - 1); j++)
        {
            if (prev[j] == inf) continue;
            ll value = prev[j] + cost(j + 1, mid);
            if (value < cur[mid])
            {
                cur[mid] = value;
                opt[mid] = j;
            }
        }
        assert(opt[mid] != -1);
        self(self, l, mid - 1, lo, opt[mid]);
        self(self, mid + 1, r, opt[mid], hi);
    };
    solve(solve, first, n, first - 1, n - 1);
    return cur;
}
// END monotone_dp_layer

// BEGIN knuth_interval_dp
template<class Cost>
vector<vector<long long>> knuth_interval_dp(int n, Cost cost,
                                            vector<vector<int>> &opt)
{
    using ll = long long;
    constexpr ll inf = LLONG_MAX / 4;
    assert(n >= 1);
    vector<vector<ll>> f(n + 1, vector<ll>(n + 1, inf));
    opt.assign(n + 1, vector<int>(n + 1, -1));
    for (int i = 1; i <= n; i++)
    {
        f[i][i] = 0;
        opt[i][i] = i;
    }
    for (int len = 2; len <= n; len++)
        for (int l = 1, r = len; r <= n; l++, r++)
        {
            ll w = cost(l, r);
            int hi = min(opt[l + 1][r], r - 1);
            for (int k = opt[l][r - 1]; k <= hi; k++)
            {
                ll value = f[l][k] + f[k + 1][r] + w;
                if (value < f[l][r])
                {
                    f[l][r] = value;
                    opt[l][r] = k;
                }
            }
        }
    return f;
}
// END knuth_interval_dp
