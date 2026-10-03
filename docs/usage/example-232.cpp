int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    using Z = mint<>;
    Z::set_mod(998244353);
    PotentialDSU<Z> d(n);
    while (q--)
    {
        int t, u, v;
        cin >> t >> u >> v;
        if (t == 0)
        {
            int x;
            cin >> x;
            cout << d.merge(u, v, Z(x)) << '\n';
        }
        else
        {
            auto x = d.diff(u, v);
            cout << (x ? x->v : -1) << '\n';
        }
    }
}
