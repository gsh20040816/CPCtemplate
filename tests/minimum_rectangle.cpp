#include "../src/compact/minimum_rectangle.hpp"

int main()
{
    int t;
    cin >> t;
    while (t--)
    {
        int n;
        cin >> n;
        vector<RealPlane::Point> p(n);
        for (auto &v : p)
            cin >> v.x >> v.y;
        auto [area, box] = minimum_rectangle(p);
        cout << setprecision(22) << area;
        for (auto v : box)
            cout << ' ' << v.x << ' ' << v.y;
        cout << '\n';
    }
}
