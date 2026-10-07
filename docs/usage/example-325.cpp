int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    while (t--)
    {
        string s;
        cin >> s;
        int n = (int)s.size();
        vector<vector<long long>> ans(n, vector<long long>(n));
        for (int l = 0; l < n; l++)
        {
            SuffixAutomaton sam;
            long long sum = 0;
            for (int r = l; r < n; r++)
            {
                sam.extend(s[r] - 'a');
                int u = sam.last;
                sum += sam.a[u].len - sam.a[sam.a[u].link].len;
                ans[l][r] = sum;
            }
        }
        int q;
        cin >> q;
        while (q--)
        {
            int l, r;
            cin >> l >> r;
            cout << ans[l - 1][r - 1] << '\n';
        }
    }
}
