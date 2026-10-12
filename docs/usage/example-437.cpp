int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    PersistentParityIndex tree(n);
    while (q--)
    {
        int op, a, b;
        cin >> op >> a >> b;
        if (op == 1)
        {
            long long delta;
            cin >> delta;
            cout << tree.add(a, b, delta) << '\n';
        }
        else if (op == 2)
        {
            long long k;
            cin >> k;
            cout << tree.stop(a, b, k) << '\n';
        }
        else if (op == 3)
        {
            long long k;
            cin >> k;
            auto result = tree.odd_kth(a, b, k);
            cout << result[0] << ' ' << result[1] << ' ' << result[2] << '\n';
        }
        else
        {
            auto result = tree.difference(a, b);
            cout << result[0] << ' ' << result[1] << '\n';
        }
    }
}
