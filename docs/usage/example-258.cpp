int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    OnlineSAM sam;
    for (int i = 0; i < n; i++)
    {
        string s;
        cin >> s;
        int p = 0;
        for (char c : s) p = sam.extend(p, c - 'a');
    }
    cout << sam.total << '\n';
    cout << sam.a.size() << '\n';
}
