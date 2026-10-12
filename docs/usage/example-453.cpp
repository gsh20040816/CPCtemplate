int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    BivariateInverse::Matrix a(n, vector<BivariateInverse::Z>(m));
    for (auto &row : a)
        for (auto &x : row)
        {
            int value;
            cin >> value;
            x = value;
        }
    auto b = BivariateInverse::inverse(a, n, m);
    for (const auto &row : b)
    {
        for (int j = 0; j < m; j++)
            cout << row[j].v << " \n"[j + 1 == m];
    }
}
