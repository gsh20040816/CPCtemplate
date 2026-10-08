int main()
{
    using G = RealSpace;
    G::Point a, b;
    G::R h, k;
    cout << fixed << setprecision(15);
    while (cin >> a.x >> a.y >> a.z >> h >> b.x >> b.y >> b.z >> k)
    {
        auto f = Plane3::equation(a, h);
        auto g = Plane3::equation(b, k);
        cout << G::angle(f.n, g.n) << '\n';
        Line3 l;
        int type = f.intersect(g, l);
        cout << type << '\n';
        if (type == 1)
        {
            cout << l.p.x << ' ' << l.p.y << ' ' << l.p.z << '\n';
            cout << l.d.x << ' ' << l.d.y << ' ' << l.d.z << '\n';
        }
    }
    return 0;
}
