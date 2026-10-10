int main()
{
    int n, m;
    cin >> n >> m;
    MinCycle g(n);
    while (m--)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        g.add(u, v, w);
    }
    auto ans = g.solve();
    if (!ans)
    {
        cout << "NONE\n";
        return 0;
    }
    auto w = ans->weight;
    string out;
    do
    {
        out += char('0' + w % 10);
        w /= 10;
    } while (w);
    reverse(out.begin(), out.end());
    cout << out << '\n';
    cout << ans->vertices.size() << '\n';
    for (int u : ans->vertices)
        cout << u << ' ';
    cout << '\n';
    for (int id : ans->edges)
        cout << id << ' ';
    cout << '\n';
}
