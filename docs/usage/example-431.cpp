int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    PersistentWeightedIndex tree(n);
    while (q--)
    {
        int op, version;
        cin >> op >> version;
        if (op == 1)
        {
            int pos;
            long long weight;
            cin >> pos >> weight;
            cout << tree.add(version, pos, weight) << '\n';
        }
        else if (op == 2)
        {
            int l, r;
            cin >> l >> r;
            auto [count, sum] = tree.query(version, l, r);
            cout << count << ' ' << sum << '\n';
        }
        else
        {
            int after, key;
            cin >> after >> key;
            if (op == 3)
                cout << tree.first(version, after, key) << '\n';
            else
                cout << tree.last(version, after, key) << '\n';
        }
    }
}
