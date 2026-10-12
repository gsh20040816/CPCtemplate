int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    HLD h(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        cin >> u >> v;
        h.add(u, v);
    }
    h.build();
    ColorComponents tree(h);
    int q;
    cin >> q;
    while (q--)
    {
        int op, u;
        cin >> op >> u;
        if (op == 0) cout << tree.query(u) << '\n';
        else tree.flip(u);
    }
}
