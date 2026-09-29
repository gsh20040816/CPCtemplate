#include "../src/compact/polygon_contains.hpp"
#include "../src/compact/convex_contains_i64.hpp"

int main()
{
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n, q, convex;
        cin >> n >> q >> convex;
        vector<IntegerPlane::Point> p(n);
        for (auto &v : p) cin >> v.x >> v.y;
        while (q--)
        {
            IntegerPlane::Point v;
            cin >> v.x >> v.y;
            if (convex == 2)
                cout << convex_contains_i64(p, v) << '\n';
            else
            {
                cout << polygon_contains(p, v);
                if (convex) cout << ' ' << convex_contains_i64(p, v);
                cout << '\n';
            }
        }
    }
}
