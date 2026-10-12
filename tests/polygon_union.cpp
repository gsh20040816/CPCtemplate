#include "../src/compact/polygon_union.hpp"

int main()
{
    int cases;
    cin >> cases;
    while (cases--)
    {
        int n;
        cin >> n;
        vector<vector<IntegerPlane::Point>> a(n);
        for (auto &p : a)
        {
            int m;
            cin >> m;
            p.resize(m);
            for (auto &v : p) cin >> v.x >> v.y;
        }
        cout << setprecision(22) << polygon_union_area(a) << '\n';
    }
}
