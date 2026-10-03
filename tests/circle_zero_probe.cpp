#include "../src/compact/line_circle_intersections.hpp"
#include "../src/compact/circle_intersections.hpp"

int main()
{
#ifdef __FAST_MATH__
#error This test requires normal floating arithmetic
#endif
    using G = RealPlane;
    static_assert(numeric_limits<G::R>::radix == 2 && numeric_limits<G::R>::digits >= 64);
    assert(fegetround() == FE_TONEAREST);
    cout << setprecision(numeric_limits<G::R>::max_digits10);
    char op;
    long double eps;
    while (cin >> op >> eps)
    {
        G::Result ans;
        if (op == 'L')
        {
            G::Point a, b;
            G::Circle c;
            cin >> a.x >> a.y >> b.x >> b.y >> c.o.x >> c.o.y >> c.r;
            ans = line_circle_intersections(a, b, c, eps);
        }
        else
        {
            G::Circle a, b;
            cin >> a.o.x >> a.o.y >> a.r >> b.o.x >> b.o.y >> b.r;
            ans = circle_intersections(a, b, eps);
        }
        sort(ans.p.begin(), ans.p.end(), [](auto a, auto b) { return tie(a.x, a.y) < tie(b.x, b.y); });
        cout << int(ans.kind) << ' ' << ans.p.size();
        for (auto p : ans.p) cout << ' ' << p.x << ' ' << p.y;
        cout << '\n';
    }
}
