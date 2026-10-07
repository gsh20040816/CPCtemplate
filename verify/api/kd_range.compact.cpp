#include "../../src/compact/kd_range.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<KDRange::Item> points(n);
    for (auto &v : points) cin >> v.p[0] >> v.p[1] >> v.id;
    KDRange tree(points);
    while (m--)
    {
        int op;
        cin >> op;
        if (op == 1)
        {
            KDRange::Item v;
            cin >> v.p[0] >> v.p[1] >> v.id;
            tree.add(v);
        }
        else
        {
            KDRange::Point low, high;
            cin >> low[0] >> low[1] >> high[0] >> high[1];
            auto removed = tree.extract(low, high);
            vector<int> ids;
            for (auto v : removed) ids.push_back(v.id);
            sort(ids.begin(), ids.end());
            cout << ids.size();
            for (int id : ids) cout << ' ' << id;
            cout << '\n';
        }
    }
}
