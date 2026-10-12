#include "../src/compact/circle_union.hpp"

int main()
{
    int cases;
    cin >> cases;
    while (cases--)
    {
        int n;
        cin >> n;
        vector<RealPlane::Circle> a(n);
        for (auto &c : a) cin >> c.o.x >> c.o.y >> c.r;
        cout << setprecision(22) << circle_union_area(a) << '\n';
    }
}
