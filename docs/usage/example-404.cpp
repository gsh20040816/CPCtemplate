int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    while (t--)
    {
        int n, m, k;
        cin >> n >> m >> k;
        vector<string> a(n);
        for (auto &row : a) cin >> row;
        cout << grid_cycles<ModInt<1000000007>>(a, k).v << '\n';
    }
}
