int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using Z = StaticMod64<UINT64_MAX>;
    int q;
    cin >> q;
    while (q--)
    {
        long long a;
        uint64_t b, k;
        cin >> a >> b >> k;
        Z x(a), y(b);
        auto inv = y.try_inv();
        cout << x.v << ' ' << y.v << ' ';
        cout << (x + y).v << ' ' << (x - y).v << ' ';
        cout << (x * y).v << ' ' << x.pow(k).v << ' ';
        if (inv)
            cout << inv->v << '\n';
        else
            cout << -1 << '\n';
    }
}
