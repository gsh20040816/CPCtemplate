#include <iostream>
#include "../src/compact/convex_tangents_i64.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    while (t--)
    {
        int n, m;
        cin >> n >> m;
        vector<IntegerPlane::Point> p(n);
        for (auto &v : p) cin >> v.x >> v.y;
        auto before = p;
        while (m--)
        {
            IntegerPlane::Point q;
            cin >> q.x >> q.y;
            auto ans = convex_tangents_i64(p, q);
            auto repeat = convex_tangents_i64(p, q);
            cout << (ans ? ans->first : -1) << ' ' << (ans ? ans->second : -1)
                 << ' ' << (ans == repeat) << '\n';
        }
        cout << "UNCHANGED " << (p == before) << '\n';
    }
}
