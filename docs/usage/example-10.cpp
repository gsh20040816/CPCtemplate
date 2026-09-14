int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    SequenceTreap g;
    for (int i = 1; i <= n; i++) g.insert(i - 1, i);
    while (m--)
    {
        int l, r;
        cin >> l >> r;
        g.reverse(l, r);
    }
    for (long long x : g.values()) cout << x << ' ';
    cout << '\n';
}
