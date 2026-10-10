#pragma once
#include <array>
#include <cassert>
#include <string>
#include <vector>
using namespace std;

struct StringHash
{
    using H = array<int, 2>;
    static constexpr H mod = {1000000007, 1000000009};
    int n;
    H base;
    vector<H> pw, pre, rev;

    StringHash(const string &s, H b)
        : n(s.size()), base(b), pw(n + 1), pre(n + 1), rev(n + 1)
    {
        pw[0] = {1, 1};
        for (int j = 0; j < 2; j++)
        {
            assert(257 <= base[j] && base[j] <= mod[j] - 2);
            for (int i = 0; i < n; i++)
            {
                int x = (unsigned char)s[i] + 1;
                int y = (unsigned char)s[n - 1 - i] + 1;
                pw[i + 1][j] = 1LL * pw[i][j] * base[j] % mod[j];
                pre[i + 1][j] = (1LL * pre[i][j] * base[j] + x) % mod[j];
                rev[i + 1][j] = (1LL * rev[i][j] * base[j] + y) % mod[j];
            }
        }
    }

    H get(int l, int r, bool reversed = false) const
    {
        assert(0 <= l && l <= r && r <= n);
        if (reversed)
        {
            int x = n - r;
            r = n - l;
            l = x;
        }
        const auto &h = reversed ? rev : pre;
        H ans;
        for (int j = 0; j < 2; j++)
        {
            long long x = h[r][j] - 1LL * h[l][j] * pw[r - l][j] % mod[j];
            ans[j] = (x + mod[j]) % mod[j];
        }
        return ans;
    }

    H join(H a, H b, int len_b) const
    {
        assert(0 <= len_b && len_b <= n);
        for (int j = 0; j < 2; j++)
        {
            a[j] = (1LL * a[j] * pw[len_b][j] + b[j]) % mod[j];
        }
        return a;
    }
};
