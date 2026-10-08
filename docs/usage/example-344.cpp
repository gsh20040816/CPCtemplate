int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m)
    {
        assert(0 <= n && 1 <= m && m < INT_MAX);
        string s(n, 0), t(m, 0);
        for (char &c : s)
        {
            int x;
            cin >> x;
            assert(0 <= x && x < 256);
            c = x;
        }
        for (char &c : t)
        {
            int x;
            cin >> x;
            assert(0 <= x && x < 256);
            c = x;
        }
        auto p = prefix_function(t);
        vector<int> nextval(m + 1, -1);
        for (int i = 1; i < m; i++)
        {
            int j = p[i - 1];
            nextval[i] = t[i] == t[j] ? nextval[j] : j;
        }
        nextval[m] = p[m - 1];
        for (int x : nextval)
            cout << x << ' ';
        cout << '\n';
        vector<int> positions;
        int j = 0;
        for (int i = 0; i < n; i++)
        {
            while (j != -1 && s[i] != t[j])
                j = nextval[j];
            j++;
            if (j == m)
            {
                positions.push_back(i - m + 1);
                j = nextval[m];
            }
        }
        cout << positions.size() << '\n';
        for (int x : positions)
            cout << x << ' ';
        cout << '\n';
    }
    return 0;
}
