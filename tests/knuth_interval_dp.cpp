#include "../src/compact/monotone_dp.hpp"
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <random>
using namespace std;
using ll = long long;

void check(bool ok)
{
    if (!ok) abort();
}

// Random costs that satisfy the quadrangle inequality and interval monotonicity:
// nonnegative pair weights inside [l,r], plus a convex nondecreasing function of a
// positive interval sum, plus a positive interval sum.
struct RandomCost
{
    int n;
    vector<vector<ll>> w;
    RandomCost(int n, mt19937 &rng) : n(n), w(n + 1, vector<ll>(n + 1))
    {
        vector<vector<ll>> pair(n + 2, vector<ll>(n + 2));
        vector<ll> s(n + 1);
        int mode = rng() % 4;
        for (int i = 1; i <= n; i++)
        {
            s[i] = s[i - 1] + 1 + rng() % 9;
            for (int j = i + 1; j <= n; j++) pair[i][j] = mode & 1 ? rng() % 6 : 0;
        }
        for (int l = 1; l <= n; l++)
            for (int r = l; r <= n; r++)
            {
                ll value = 0;
                for (int i = l; i <= r; i++)
                    for (int j = i + 1; j <= r; j++) value += pair[i][j];
                ll t = s[r] - s[l - 1];
                if (mode & 2) value += t * t;
                value += t;
                w[l][r] = value;
            }
    }
};

// Direct O(n^3) interval DP with the same smallest-optimum tie rule.
void cubic(int n, const vector<vector<ll>> &w, vector<vector<ll>> &f,
           vector<vector<int>> &opt)
{
    f.assign(n + 1, vector<ll>(n + 1, LLONG_MAX / 4));
    opt.assign(n + 1, vector<int>(n + 1, -1));
    for (int i = 1; i <= n; i++)
    {
        f[i][i] = 0;
        opt[i][i] = i;
    }
    for (int len = 2; len <= n; len++)
        for (int l = 1, r = len; r <= n; l++, r++)
            for (int k = l; k < r; k++)
            {
                ll value = f[l][k] + f[k + 1][r] + w[l][r];
                if (value < f[l][r])
                {
                    f[l][r] = value;
                    opt[l][r] = k;
                }
            }
}

// Independent stone-merging oracle: try every sequence of adjacent merges.
ll merge_orders(vector<ll> a, map<vector<ll>, ll> &memo)
{
    if (a.size() == 1) return 0;
    auto it = memo.find(a);
    if (it != memo.end()) return it->second;
    ll best = LLONG_MAX;
    for (int i = 0; i + 1 < (int)a.size(); i++)
    {
        vector<ll> b = a;
        b[i] += b[i + 1];
        b.erase(b.begin() + i + 1);
        best = min(best, b[i] + merge_orders(b, memo));
    }
    return memo[a] = best;
}

int main()
{
    mt19937 rng(20261015);
    long long cells = 0;
    for (int test = 0; test < 600; test++)
    {
        int n = 1 + rng() % 40;
        RandomCost c(n, rng);
        int calls = 0;
        auto cost = [&](int l, int r)
        {
            check(1 <= l && l < r && r <= n);
            calls++;
            return c.w[l][r];
        };
        vector<vector<int>> opt, want_opt;
        vector<vector<ll>> want;
        auto f = knuth_interval_dp(n, cost, opt);
        cubic(n, c.w, want, want_opt);
        check(calls == n * (n - 1) / 2);
        for (int l = 1; l <= n; l++)
            for (int r = l; r <= n; r++)
            {
                check(f[l][r] == want[l][r]);
                check(opt[l][r] == want_opt[l][r]);
                if (l < r) check(opt[l][r - 1] <= opt[l][r] && opt[l][r] <= opt[l + 1][r]);
                cells++;
            }
        // Yao's lemma: the DP values also satisfy the quadrangle inequality.
        for (int a = 1; a <= n; a++)
            for (int b = a; b <= n; b++)
                for (int d = b; d <= n; d++)
                {
                    int cc = b + rng() % (d - b + 1);
                    check(f[a][cc] + f[b][d] <= f[a][d] + f[b][cc]);
                }
    }
    for (int test = 0; test < 300; test++)
    {
        int n = 1 + rng() % 8;
        vector<ll> a(n + 1), s(n + 1);
        for (int i = 1; i <= n; i++)
        {
            a[i] = 1 + rng() % 20;
            s[i] = s[i - 1] + a[i];
        }
        vector<vector<int>> opt;
        auto f = knuth_interval_dp(n, [&](int l, int r) { return s[r] - s[l - 1]; }, opt);
        map<vector<ll>, ll> memo;
        check(f[1][n] == merge_orders(vector<ll>(a.begin() + 1, a.end()), memo));
    }
    // Negative control: w(l,r)=-[l=1] meets the quadrangle inequality with equality but
    // breaks interval monotonicity; the true f(1,4)=-3 lies outside Knuth's range.
    {
        vector<vector<ll>> w(5, vector<ll>(5));
        for (int r = 1; r <= 4; r++) w[1][r] = -1;
        vector<vector<int>> opt, want_opt;
        vector<vector<ll>> want;
        auto f = knuth_interval_dp(4, [&](int l, int r) { return w[l][r]; }, opt);
        cubic(4, w, want, want_opt);
        check(want[1][4] == -3 && f[1][4] == -2 && want_opt[2][4] == 2 && want_opt[1][4] == 3);
    }
    // Largest stone-merging case: n=3000, weights 1e9; the answer fits in long long.
    int n = 3000;
    vector<ll> s(n + 1);
    for (int i = 1; i <= n; i++) s[i] = s[i - 1] + 1000000000;
    vector<vector<int>> opt;
    auto f = knuth_interval_dp(n, [&](int l, int r) { return s[r] - s[l - 1]; }, opt);
    check(f[1][n] > 0 && f[1][n] < LLONG_MAX / 4);
    cout << cells << " Knuth cells and optima match O(n^3), merge orders, n=3000 PASS\n";
}
