int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using Z = ModInt<998244353>;
    int n;
    cin >> n;
    vector<vector<Z>> a(n, vector<Z>(n));
    for (auto &row : a)
        for (auto &x : row) cin >> x.v;
    cout << det_prime<998244353>(move(a)).v << '\n';
}
