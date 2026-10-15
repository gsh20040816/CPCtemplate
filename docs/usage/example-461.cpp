int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<long long> a(n), sum(2 * n);
    for (auto &x : a) cin >> x;
    // Break the circle: positions 1..2n-1 repeat a, every window of n is a line.
    for (int i = 1; i < 2 * n; i++) sum[i] = sum[i - 1] + a[(i - 1) % n];
    auto cost = [&](int l, int r) { return sum[r] - sum[l - 1]; };
    vector<vector<int>> opt;
    auto f = knuth_interval_dp(2 * n - 1, cost, opt);
    long long answer = f[1][n];
    for (int i = 2; i <= n; i++) answer = min(answer, f[i][i + n - 1]);
    cout << answer << '\n';
}
