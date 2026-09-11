#include "../src/compact/weighted_matching.hpp"
#include "../src/classic/weighted_matching.hpp"
using I = __int128_t;
using Matrix = vector<vector<optional<long long>>>;
constexpr I inf = I(1) << 120;

optional<I> oracle(const Matrix &a, int m, bool skip)
{
    vector<I> dp(1 << m, -inf);
    dp[0] = 0;
    for (const auto &row : a)
    {
        vector<I> next(1 << m, -inf);
        for (int mask = 0; mask < (1 << m); mask++)
        {
            if (dp[mask] == -inf)
                continue;
            if (skip)
                next[mask] = max(next[mask], dp[mask]);
            for (int j = 0; j < m; j++)
                if (!(mask >> j & 1) && row[j])
                    next[mask | (1 << j)] = max(next[mask | (1 << j)], dp[mask] + *row[j]);
        }
        dp.swap(next);
    }
    I best = *max_element(dp.begin(), dp.end());
    if (best == -inf)
        return nullopt;
    return best;
}

template <class G>
void certificate(const G &g, const Matrix &a, optional<I> result, bool skip)
{
    int n = a.size();
    if (!result)
    {
        for (int i = 1; i <= n; i++)
            assert(g.l[i] == 0);
        for (int j = 1; j <= g.m; j++)
            assert(g.r[j] == 0);
        return;
    }
    I sum = 0;
    vector<bool> seen(g.m + 1);
    for (int i = 1; i <= n; i++)
    {
        int j = g.l[i];
        if (!j)
        {
            assert(skip);
            continue;
        }
        assert(1 <= j && j <= g.m && !seen[j]);
        assert(a[i - 1][j - 1] && g.r[j] == i);
        sum += *a[i - 1][j - 1];
        seen[j] = true;
    }
    for (int j = 1; j <= g.m; j++)
    {
        int i = g.r[j];
        assert((i != 0) == seen[j]);
        if (i)
            assert(1 <= i && i <= n && g.l[i] == j);
    }
    assert(sum == *result);
}

void check(const Matrix &a, int m)
{
    int n = a.size();
    WeightedMatching g(n, m);
    Weighted_Matching<8, 8> h;
    h.Init(n, m);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            if (a[i][j])
            {
                g.add(i + 1, j + 1, *a[i][j]);
                h.Insert(i + 1, j + 1, *a[i][j]);
                g.add(i + 1, j + 1, LLONG_MIN);
                h.Insert(i + 1, j + 1, LLONG_MIN);
            }
    for (bool skip : {false, true, false})
    {
        auto want = oracle(a, m, skip);
        auto x = g.solve(skip);
        auto y = h.Solve(skip);
        assert(x == want && y == want);
        certificate(g, a, x, skip);
        certificate(h, a, y, skip);
    }
    h.Init(n, m);
    assert(h.Solve(true) == optional<I>(0));
    assert(h.Solve(false).has_value() == (n == 0));
}

int main()
{
    for (int n = 0; n <= 3; n++)
        for (int m = 0; m <= 3; m++)
        {
            int states = 1;
            for (int i = 0; i < n * m; i++)
                states *= 3;
            for (int mask = 0; mask < states; mask++)
            {
                int code = mask;
                Matrix a(n, vector<optional<long long>>(m));
                for (auto &row : a)
                    for (auto &x : row)
                    {
                        int digit = code % 3;
                        code /= 3;
                        if (digit)
                            x = digit == 1 ? -2 : 3;
                    }
                check(a, m);
            }
        }
    mt19937_64 rng(6577);
    vector<long long> special{LLONG_MIN, LLONG_MIN + 1, -1, 0, 1, LLONG_MAX - 1, LLONG_MAX};
    for (int it = 0; it < 2000; it++)
    {
        int n = rng() % 9;
        int m = rng() % 9;
        Matrix a(n, vector<optional<long long>>(m));
        for (auto &row : a)
            for (auto &x : row)
                if (rng() % 3)
                    x = special[rng() % special.size()];
        check(a, m);
    }
    // Equal-weight dense input forces long alternating paths in the tie order.
    static Weighted_Matching<500, 500> h;
    WeightedMatching g(500, 500);
    h.Init(500, 500);
    for (int i = 1; i <= 500; i++)
        for (int j = 1; j <= 500; j++)
        {
            g.add(i, j, LLONG_MIN);
            h.Insert(i, j, LLONG_MIN);
        }
    assert(g.solve() == optional<I>(I(500) * LLONG_MIN));
    assert(h.Solve() == optional<I>(I(500) * LLONG_MIN));
    // A later edge must allow a fresh solution; full-mode failure clears the old plan.
    WeightedMatching dynamic(2, 2);
    dynamic.add(1, 1, 3);
    assert(dynamic.solve(true) == optional<I>(3));
    assert(!dynamic.solve());
    assert(dynamic.l[1] == 0 && dynamic.r[1] == 0);
    dynamic.add(2, 1, 7);
    dynamic.add(1, 2, -1);
    assert(dynamic.solve() == optional<I>(6));
    assert(dynamic.solve(true) == optional<I>(7));
    cout << "Weighted matching dual exhaustive missing-edge graphs, subset DP, int64 extremes and dense ties PASS\n";
}
