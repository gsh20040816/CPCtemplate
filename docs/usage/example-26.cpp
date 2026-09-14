int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using M = ModMatrix<998244353>;
    int n, m, k;
    cin >> n >> m >> k;
    M::Matrix a(n, vector<M::Z>(m)), b(m, vector<M::Z>(k));
    for (auto &row : a)
        for (auto &x : row) cin >> x.v;
    for (auto &row : b)
        for (auto &x : row) cin >> x.v;
    auto c = M::multiply(a, b);
    for (auto &row : c)
        for (int j = 0; j < k; j++) cout << row[j].v << (j + 1 == k ? '\n' : ' ');
}
