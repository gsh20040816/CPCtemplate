int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    Kruskal g(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        g.add(u, v, w);
    }
    cout << g.run() << ' ';
    __int128 x = g.weight;
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
    cout << a << ' ' << g.ids.size();
    for (int id : g.ids) cout << ' ' << id;
    cout << '\n';
}
