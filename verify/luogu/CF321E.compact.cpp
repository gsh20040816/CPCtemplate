#include <iostream>
#include "../../src/compact/monotone_dp.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k;
    cin >> n >> k;
    vector<vector<int>> sum(n + 1, vector<int>(n + 1));
    for (int i = 1; i <= n; i++)
    {
        for (int j = 1; j <= n; j++)
        {
            char c;
            cin >> c;
            sum[i][j] = c - '0' + sum[i - 1][j] + sum[i][j - 1] - sum[i - 1][j - 1];
        }
    }
    auto cost = [&](int l, int r) -> long long
    {
        return (sum[r][r] - sum[l - 1][r] - sum[r][l - 1] + sum[l - 1][l - 1]) / 2;
    };
    vector<long long> dp(n + 1, LLONG_MAX / 4);
    vector<int> opt;
    dp[0] = 0;
    for (int g = 1; g <= k; g++)
    {
        dp = monotone_dp_layer(dp, g, cost, opt);
    }
    cout << dp[n] << '\n';
}
