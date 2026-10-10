int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, root, q;
    cin >> n >> root >> q;
    LongChain tree(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        cin >> u >> v;
        tree.add(u, v);
    }
    tree.build(root);
    while (q--)
    {
        int u, k;
        cin >> u >> k;
        cout << tree.kth(u, k) << '\n';
    }
}
