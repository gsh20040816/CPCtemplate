// https://judge.yosupo.jp/problem/rectangle_sum
#include "../../src/compact/offline_rectangle_sum.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<array<long long, 3>> points(n);
    vector<array<long long, 4>> queries(q);
    for (auto &p : points)
        cin >> p[0] >> p[1] >> p[2];
    for (auto &r : queries)
        cin >> r[0] >> r[1] >> r[2] >> r[3];
    for (auto answer : offline_rectangle_sum(points, queries))
        cout << answer << '\n';
}
