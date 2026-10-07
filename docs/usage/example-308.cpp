int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, s;
    cin >> n >> m >> s;
    ShortestPathTree t(n);
    while (m--)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        t.add(u, v, w);
    }
    int reached = t.run(s);
    auto print = [](__int128 x)
    {
        if (x < 0)
        {
            cout << '-';
            x = -x;
        }
        string a;
        do
        {
            a += char('0' + x % 10);
            x /= 10;
        } while (x);
        reverse(a.begin(), a.end());
        cout << a;
    };
    cout << reached << ' ';
    print(t.weight);
    cout << ' ' << t.ids.size();
    for (int id : t.ids) cout << ' ' << id;
    cout << '\n';
    for (int u = 1; u <= n; u++)
    {
        if (t.dis[u] == ShortestPathTree::inf) cout << "INF\n";
        else
        {
            auto path = t.path(u);
            print(t.dis[u]);
            cout << ' ' << path.size();
            for (int id : path) cout << ' ' << id;
            cout << '\n';
        }
    }
}
