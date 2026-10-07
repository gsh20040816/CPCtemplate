int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int m;
    cin >> m;
    KDTreeSum<> tree(m);
    while (m--)
    {
        int op, x, y;
        cin >> op >> x >> y;
        if (op == 1) tree.add(x, y, 1);
        else cout << tree.query(INT_MIN, INT_MIN, x, y) << '\n';
    }
}
