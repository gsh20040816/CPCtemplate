#include "../src/compact/circle_coverage.hpp"

int main()
{
    int t;
    cin >> t;
    while (t--)
    {
        int n;
        cin >> n;
        vector<RealPlane::Circle> a(n);
        for (auto &c : a)
            cin >> c.o.x >> c.o.y >> c.r;
        auto ans = circle_coverage_area(a);
        if (ans.size() != a.size() + 1 || ans[0] != 0)
            abort();
        for (auto x : ans)
            cout << setprecision(22) << x << ' ';
        cout << '\n';
    }
}
