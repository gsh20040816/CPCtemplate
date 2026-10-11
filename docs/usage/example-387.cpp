int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    bool strict;
    cin >> n >> strict;
    vector<array<long long, 4>> p(n);
    for (auto &point : p)
        for (auto &x : point) cin >> x;
    auto count = Dominance4D::count(p, strict);
    for (int value : count) cout << value << '\n';
}
