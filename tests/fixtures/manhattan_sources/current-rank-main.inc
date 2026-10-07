int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k;
    while (cin >> n >> k && n)
    {
        vector<ManhattanMST::Point> p(n);
        for (auto &[x, y] : p)
            cin >> x >> y;
        auto tree = ManhattanMST::solve(p);
        vector<ManhattanMST::I> w;
        for (auto [u, v] : tree.edges)
        {
            ManhattanMST::I x = ManhattanMST::I(p[u].first) - p[v].first;
            ManhattanMST::I y = ManhattanMST::I(p[u].second) - p[v].second;
            w.push_back((x < 0 ? -x : x) + (y < 0 ? -y : y));
        }
        sort(w.begin(), w.end());
        // This source-protocol adapter only uses coordinates in [-100000,100000].
        cout << (long long)w[n - k - 1] << '\n';
    }
}
