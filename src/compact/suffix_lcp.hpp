#pragma once
#include "string.hpp"

// BEGIN SuffixLCP
struct SuffixLCP
{
    int n;
    vector<int> rk, lg;
    vector<vector<int>> st;

    SuffixLCP(const SuffixArray &suffix)
    {
        init(suffix);
    }

    void init(const SuffixArray &suffix)
    {
        n = suffix.sa.size();
        rk = suffix.rk;
        lg.assign(n + 1, 0);
        for (int i = 2; i <= n; i++)
            lg[i] = lg[i / 2] + 1;
        st.assign(lg[n] + 1, {});
        st[0] = suffix.lcp;
        for (int k = 1; k <= lg[n]; k++)
        {
            int len = 1 << k;
            st[k].resize(n - len + 1);
            for (int i = 0; i <= n - len; i++)
                st[k][i] = min(st[k - 1][i], st[k - 1][i + len / 2]);
        }
    }

    int query(int x, int y) const
    {
        assert(0 <= x && x <= n && 0 <= y && y <= n);
        if (x == y || x == n || y == n)
            return n - max(x, y);
        int a = rk[x], b = rk[y];
        if (a > b)
            swap(a, b);
        int k = lg[b - a];
        return min(st[k][a + 1], st[k][b - (1 << k) + 1]);
    }

    // Compare [l1,r1) and [l2,r2); return -1, 0 or 1.
    int compare(int l1, int r1, int l2, int r2) const
    {
        assert(0 <= l1 && l1 <= r1 && r1 <= n);
        assert(0 <= l2 && l2 <= r2 && r2 <= n);
        int a = r1 - l1, b = r2 - l2;
        if (query(l1, l2) >= min(a, b))
            return (a > b) - (a < b);
        return rk[l1] < rk[l2] ? -1 : 1;
    }
};

// END SuffixLCP

// BEGIN prefix_lcs
// reversed must be built on the reversed original sequence.
inline int prefix_lcs(const SuffixLCP &reversed, int x, int y)
{
    assert(0 <= x && x <= reversed.n && 0 <= y && y <= reversed.n);
    return reversed.query(reversed.n - x, reversed.n - y);
}

// END prefix_lcs

// BEGIN square_counts
// Count nonempty squares AA by their starting and ending positions.
inline pair<vector<long long>, vector<long long>>
square_counts(const SuffixLCP &forward, const SuffixLCP &reversed)
{
    int n = forward.n;
    assert(reversed.n == n);
    vector<long long> start(n + 1), finish(n + 1);
    for (int len = 1; len <= n / 2; len++)
        for (int i = 0; i < n - len; i += len)
        {
            int j = i + len;
            int left = min(len - 1, prefix_lcs(reversed, i, j));
            int right = min(len, forward.query(i, j));
            if (left + right < len)
                continue;
            int l = i - left, r = i + right - len;
            start[l]++;
            start[r + 1]--;
            finish[l + 2 * len - 1]++;
            finish[r + 2 * len]--;
        }
    for (int i = 1; i < n; i++)
    {
        start[i] += start[i - 1];
        finish[i] += finish[i - 1];
    }
    start.resize(n);
    finish.resize(n);
    return {start, finish};
}

// END square_counts
