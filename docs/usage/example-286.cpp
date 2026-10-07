int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    SequenceSplay t(n);
    while (m--)
    {
        int l, r;
        cin >> l >> r;
        t.reverse(l - 1, r);
    }
    auto a = t.order();
    for (int i = 0; i < n; i++)
        cout << a[i] + 1 << (i + 1 == n ? '\n' : ' ');
}
