int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    string s;
    cin >> n >> q >> s;
    SequenceTreap tree;
    for (int i = 0; i < n; i++) tree.insert(i, s[i] - '0');
    while (q--)
    {
        int l, r;
        cin >> l >> r;
        tree.flip_bits(l, r);
    }
    for (auto bit : tree.values()) cout << bit;
    cout << '\n';
}
