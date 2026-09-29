int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s, t;
    cin >> s >> t;
    int n = s.size(), m = t.size();
    vector<int> a;
    for (char c : s) a.push_back(c - 'a');
    a.push_back(26);
    for (char c : t) a.push_back(c - 'a');
    SuffixArray suffix(a, 27);
    int best = 0, left = 0, right = 0;
    for (int k = 1; k < (int)a.size(); k++)
    {
        int x = suffix.sa[k - 1], y = suffix.sa[k];
        if (x > y) swap(x, y);
        if (x >= n || y <= n) continue;
        int len = min({suffix.lcp[k], n - x, n + 1 + m - y});
        if (len > best)
        {
            best = len;
            left = x;
            right = y - n - 1;
        }
    }
    cout << left << ' ' << left + best << ' ' << right << ' ' << right + best << '\n';
}
