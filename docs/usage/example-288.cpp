int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    SequenceSplay t(n);
    while (q--)
    {
        int op, x, y;
        cin >> op;
        if (op == 0)
        {
            cin >> x >> y;
            t.reverse(x, y);
        }
        else if (op == 1)
        {
            cin >> x;
            cout << t.pos(x) << '\n';
        }
        else if (op == 2)
        {
            cin >> x;
            cout << t.at(x) << '\n';
        }
        else
        {
            auto a = t.order();
            for (int i = 0; i < n; i++)
                cout << a[i] << (i + 1 == n ? '\n' : ' ');
            if (n == 0) cout << '\n';
        }
    }
}
