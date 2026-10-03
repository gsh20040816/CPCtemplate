#include "../src/compact/dominance_3d.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q;
    cin >> q;
    while (q--)
    {
        int n;
        cin >> n;
        vector<array<long long, 3>> p(n);
        for (auto &[x, y, z] : p) cin >> x >> y >> z;
        auto before = p;
        auto ans = Dominance3D::count(p);
        bool empty = Dominance3D::count({}).empty();
        auto pair = Dominance3D::count({{0, 0, 0}, {0, 0, 0}});
        bool repeat = ans == Dominance3D::count(p);
        cout << n << ' ' << (p == before) << ' '
             << (empty && pair == vector<int>({1, 1}) && repeat) << '\n';
        for (int x : ans) cout << x << ' ';
        cout << '\n';
    }
}
