#include "../src/compact/convex_cut.hpp"
#include "../src/compact/polygon_centroid.hpp"

int main()
{
    int t;
    cin >> t;
    cout << setprecision(22);
    while (t--)
    {
        int mode, n;
        cin >> mode >> n;
        vector<RealPlane::Point> p(n);
        for (auto &v : p)
            cin >> v.x >> v.y;
        if (mode == 0)
        {
            RealPlane::Point a, b;
            cin >> a.x >> a.y >> b.x >> b.y;
            auto q = convex_cut(p, a, b);
            cout << q.size();
            for (auto v : q)
                cout << ' ' << v.x << ' ' << v.y;
        }
        else
        {
            auto c = polygon_centroid(p);
            cout << bool(c);
            if (c)
                cout << ' ' << c->x << ' ' << c->y;
        }
        cout << '\n';
    }
}
