int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<int> parent(n), value(n);
    for (int &p : parent)
        cin >> p;
    for (int &x : value)
        cin >> x;
    XorPathSum tree(parent, value);
    cout << tree.sum() << '\n';
    while (q--)
    {
        int x, value;
        cin >> x >> value;
        cout << tree.set(x, value) << '\n';
    }
}
