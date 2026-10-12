int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<long long> a(n);
    for (auto &x : a)
        cin >> x;
    DivideSegmentTree tree(a);
    while (q--)
    {
        int type, l, r;
        cin >> type >> l >> r;
        --l;
        if (type == 3)
            cout << tree.sum(l, r) << '\n';
        else
        {
            long long x;
            cin >> x;
            if (type == 1)
                tree.divide(l, r, x);
            else
                tree.assign(l, r, x);
        }
    }
}
