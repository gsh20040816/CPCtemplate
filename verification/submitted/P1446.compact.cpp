#include <bits/stdc++.h>
#include <cassert>
using namespace std;
struct BurnsideAverage
{
    using ll = long long;
    ll order, mod, sum = 0;

    BurnsideAverage(ll g, ll p) : order(g)
    {
        assert(g > 0 && p > 0 && __int128(g) * p <= LLONG_MAX / 2);
        mod = g * p;
    }

    ll power(ll a, long long k) const
    {
        assert(a >= 0 && k >= 0);
        a %= mod;
        ll ans = 1 % mod;
        while (k)
        {
            if (k & 1) ans = __int128(ans) * a % mod;
            a = __int128(a) * a % mod;
            k >>= 1;
        }
        return ans;
    }

    void add(ll fixed, ll multiplicity = 1)
    {
        assert(fixed >= 0 && multiplicity >= 0);
        sum = (sum + __int128(fixed) * multiplicity) % mod;
    }

    ll result() const
    {
        assert(sum % order == 0);
        return sum / order;
    }
};

vector<int> permutation_cycles(const vector<int> &p)
{
    int n = p.size();
    vector<int> seen(n), lengths;
    for (int i = 0; i < n; i++)
    {
        if (seen[i]) continue;
        int u = i, len = 0;
        do
        {
            seen[u] = 1;
            len++;
            u = p[u];
        } while (u != i);
        lengths.push_back(len);
    }
    return lengths;
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int r, b, g, m, mod;
    cin >> r >> b >> g >> m >> mod;
    int n = r + b + g;
    vector<vector<int>> group(m, vector<int>(n));
    for (auto &p : group)
    {
        for (int &x : p)
        {
            cin >> x;
            x--;
        }
    }
    vector<int> identity(n);
    iota(identity.begin(), identity.end(), 0);
    group.push_back(identity);
    sort(group.begin(), group.end());
    group.erase(unique(group.begin(), group.end()), group.end());
    BurnsideAverage avg(group.size(), mod);
    for (auto &p : group)
    {
        vector<vector<long long>> dp(r + 1, vector<long long>(b + 1));
        dp[0][0] = 1;
        int used = 0;
        for (int len : permutation_cycles(p))
        {
            vector<vector<long long>> next(r + 1, vector<long long>(b + 1));
            for (int i = 0; i <= r; i++)
            {
                for (int j = 0; j <= b; j++)
                {
                    if (i + len <= r) next[i + len][j] += dp[i][j];
                    if (j + len <= b) next[i][j + len] += dp[i][j];
                    if (used - i - j + len <= g) next[i][j] += dp[i][j];
                }
            }
            for (auto &row : next)
            {
                for (auto &value : row) value %= avg.mod;
            }
            dp.swap(next);
            used += len;
        }
        avg.add(dp[r][b]);
    }
    cout << avg.result() << '\n';
}
