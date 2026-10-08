int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    while (cin >> s)
    {
        assert(s.size() <= (INT_MAX - 2) / 2);
        int len = s.size();
        int n = 2 * len + 1;
        vector<int> a(n);
        for (int i = 0; i < len; i++)
        {
            a[i] = (unsigned char)s[i] + 2;
            a[len + 1 + i] = (unsigned char)s[len - 1 - i] + 2;
        }
        a[len] = 1;
        SuffixArray suffix(a, 258);
        SuffixLCP lcp(suffix);
        int best = 0, start = 0;
        for (int i = 0; i < len; i++)
        {
            int radius = lcp.query(i, n - i);
            if (2 * radius > best)
            {
                best = 2 * radius;
                start = i - radius;
            }
            radius = lcp.query(i, n - i - 1);
            if (2 * radius - 1 > best)
            {
                best = 2 * radius - 1;
                start = i - radius + 1;
            }
        }
        cout << s.substr(start, best) << '\n';
    }
    return 0;
}
