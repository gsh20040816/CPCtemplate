int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k;
    cin >> n >> k;
    vector<long long> x(n + 1), sum(n + 1);
    for (int i = 1; i <= n; i++) cin >> x[i];
    sort(x.begin() + 1, x.end());
    for (int i = 1; i <= n; i++) sum[i] = sum[i - 1] + x[i];
    auto cost = [&](int l, int r) -> long long
    {
        int mid = (l + r) / 2;
        return x[mid] * (mid - l + 1) - (sum[mid] - sum[l - 1]) +
               (sum[r] - sum[mid]) - x[mid] * (r - mid);
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
