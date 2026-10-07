int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, alphabet;
    cin >> n >> m >> alphabet;
    vector<long long> s(n), t(m);
    for (auto &x : s) cin >> x;
    for (auto &x : t) cin >> x;
    auto ans = order_match(s, t);
    cout << ans.size() << '\n';
    for (int x : ans) cout << x + 1 << '\n';
}
