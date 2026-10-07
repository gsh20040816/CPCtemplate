int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    char offset;
    cin >> n >> q >> offset;
    AhoCorasick ac;
    vector<int> end(n);
    for (int &u : end)
    {
        string s;
        cin >> quoted(s);
        u = ac.add(s, offset);
    }
    ac.build();
    while (q--)
    {
        string s;
        cin >> quoted(s);
        auto cnt = ac.count(s, offset);
        for (int u : end) cout << cnt[u] << ' ';
        cout << '\n';
    }
}
