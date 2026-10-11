int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<array<long long, 4>> p(n);
    for (auto &point : p)
        for (auto &x : point) cin >> x;
    auto count = Dominance4D::count(p, true);
    cout << accumulate(count.begin(), count.end(), 0LL) << '\n';
}
