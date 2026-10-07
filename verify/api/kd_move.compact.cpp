#include "../../src/compact/kd_range.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    long long w, h;
    cin >> n >> q >> w >> h;
    vector<KDRange::Point> p(n);
    vector<KDRange::Item> items;
    for (int i = 0; i < n; i++)
    {
        cin >> p[i][0] >> p[i][1];
        auto [x, y] = p[i];
        items.push_back({{x + y, x - y}, i});
    }
    KDRange tree(items);
    while (q--)
    {
        long long x, y, e, a, b, c, d, f, g;
        cin >> x >> y >> e >> a >> b >> c >> d >> f >> g;
        auto removed = tree.extract({x + y - e, x - y - e},
                                    {x + y + e, x - y + e});
        for (auto v : removed)
        {
            int id = v.id;
            auto [u, t] = p[id];
            long long nx = ((__int128)u * a + (__int128)t * b + (__int128)(id + 1) * c) % w;
            long long ny = ((__int128)u * d + (__int128)t * f + (__int128)(id + 1) * g) % h;
            p[id] = {nx, ny};
            tree.add({{nx + ny, nx - ny}, id});
        }
    }
    for (auto [x, y] : p) cout << x << ' ' << y << '\n';
}
