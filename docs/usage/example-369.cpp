int main()
{
    string s;
    getline(cin, s);
    StringHash::H base;
    cin >> base[0] >> base[1];
    StringHash h(s, base);
    int q;
    cin >> q;
    while (q--)
    {
        int l, r, a, b;
        cin >> l >> r >> a >> b;
        auto x = h.get(l, r);
        auto y = h.get(l, r, true);
        auto z = h.join(x, h.get(a, b), b - a);
        cout << x[0] << ' ' << x[1] << '\n';
        cout << y[0] << ' ' << y[1] << '\n';
        cout << z[0] << ' ' << z[1] << '\n';
    }
}
