int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    if (!(cin >> n)) return 0;
    if (n == 1)
    {
        cout << 0 << '\n';
        return 0;
    }
    LinearSieve sieve(n - 1);
    long long ans = 1;
    for (int i = 1; i < n; i++) ans += 2LL * sieve.phi[i];
    cout << ans << '\n';
}
