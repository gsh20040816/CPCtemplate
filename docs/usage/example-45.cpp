int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    LinkCutTree g(n);
    for (int i = 1; i <= n; i++)
    {
        unsigned long long x;
        cin >> x;
        g.set(i, x);
    }
    while (m--)
    {
        int op, x, y;
        cin >> op >> x >> y;
        if (op == 0)
            cout << g.query(x, y) << '\n';
        else if (op == 1)
            g.link(x, y);
        else if (op == 2)
            g.cut(x, y);
        else
            g.set(x, y);
    }
}
