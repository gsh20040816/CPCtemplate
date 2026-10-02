int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    auto print = [](__int128_t x)
    {
        // Unsigned subtraction also handles the minimum signed int128 value.
        __uint128_t u = x < 0 ? __uint128_t(0) - __uint128_t(x) : __uint128_t(x);
        string s;
        do { s += char('0' + u % 10); u /= 10; } while (u);
        if (x < 0) cout << '-';
        reverse(s.begin(), s.end());
        cout << s;
    };
    int q;
    if (!(cin >> q)) return 0;
    while (q--)
    {
        IntegerGeometry3D::Point a, b, c, d;
        for (auto p : {&a, &b, &c, &d}) cin >> p->x >> p->y >> p->z;
        print(IntegerGeometry3D::orient(a, b, c, d));
        cout << ' ' << IntegerGeometry3D::collinear(a, b, c)
             << ' ' << IntegerGeometry3D::on_segment(d, a, b) << '\n';
    }
}
