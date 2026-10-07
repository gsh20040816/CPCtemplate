int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    auto [odd, even] = manacher(a);
    for (int x : odd) cout << x << ' ';
    cout << '\n';
    for (int x : even) cout << x << ' ';
    cout << '\n';
}
