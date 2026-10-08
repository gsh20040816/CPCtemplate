int main()
{
    using G = RealSpace;
    G::Point a, b, q;
    G::R rad;
    cout << fixed << setprecision(15);
    while (cin >> a.x >> a.y >> a.z >> b.x >> b.y >> b.z
               >> q.x >> q.y >> q.z >> rad)
    {
        auto l = Line3::through(a, b);
        auto p = l.projection(q);
        auto s = l.segment_projection(q);
        cout << p.x << ' ' << p.y << ' ' << p.z << '\n';
        cout << s.x << ' ' << s.y << ' ' << s.z << '\n';
        cout << l.distance(q) << ' ' << l.segment_distance(q) << '\n';
        cout << l.on_segment(q) << '\n';
        if (G::norm(l.d) > 0)
        {
            auto r = l.rotate(q, rad);
            cout << r.x << ' ' << r.y << ' ' << r.z << '\n';
        }
        else
            cout << "no axis\n";
    }
    return 0;
}
