int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k;
    cin >> n >> k;
    vector<array<long long, 3>> p(n);
    for (auto &[x, y, z] : p) cin >> x >> y >> z;
    vector<int> hist(n);
    for (int x : Dominance3D::count(p)) ++hist[x];
    for (int x : hist) cout << x << '\n';
}
