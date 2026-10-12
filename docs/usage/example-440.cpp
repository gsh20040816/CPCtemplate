int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n, q;
        cin >> n >> q;
        vector<int> parent(n, -1);
        for (int i = 1; i < n; i++)
        {
            cin >> parent[i];
            parent[i]--;
        }
        vector<long long> b(n);
        for (auto &x : b)
            cin >> x;
        DynamicPeachTree tree(parent, b);
        while (q--)
        {
            int type, x;
            long long value;
            cin >> type >> x >> value;
            cout << (tree.add(type, x - 1, value) ? "YES" : "NO") << '\n';
        }
    }
}
