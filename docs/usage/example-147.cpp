int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    DivisionTree tree(a);
    while (q--)
    {
        int l, r, k;
        cin >> l >> r >> k;
        cout << tree.kth(l, r, k) << '\n';
    }
}
