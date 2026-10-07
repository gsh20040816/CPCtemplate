int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<pair<string, long long>> patterns(n);
    for (auto &[s, w] : patterns) cin >> quoted(s) >> w;
    ACWeighted ac(patterns);
    while (q--)
    {
        string s;
        cin >> quoted(s);
        cout << ac.query(s) << '\n';
    }
}
