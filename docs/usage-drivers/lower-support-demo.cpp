#include "../../src/compact/support_hull.hpp"
#include <algorithm>
#include <iostream>
#include <string>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using P = SupportHull::Point;
    using I = __int128_t;
    int n, q;
    cin >> n >> q;
    vector<P> points(n), hull;
    for (auto &p : points) cin >> p.x >> p.y;
    auto less = [](P p, P r) { return p.x != r.x ? p.x < r.x : p.y < r.y; };
    auto dot = [](P p, long long a, long long b) { return I(a) * p.x + I(b) * p.y; };
    if (n)
    {
        P left = *min_element(points.begin(), points.end(), less), right = left;
        for (P p : points)
            if (p.x > right.x || (p.x == right.x && p.y < right.y)) right = p;
        hull = SupportHull::build(left, right, [&](long long a, long long b)
        {
            P best = points[0];
            for (P p : points)
                if (dot(p, a, b) > dot(best, a, b) ||
                    (dot(p, a, b) == dot(best, a, b) && less(p, best))) best = p;
            return best;
        });
    }
    cout << hull.size() << '\n';
    for (P p : hull) cout << p.x << ' ' << p.y << '\n';
    while (q--)
    {
        long long a, b;
        cin >> a >> b; // Custom contract: b <= 0; upward support is excluded.
        if (hull.empty()) { cout << "EMPTY\n"; continue; }
        int l = 0, r = int(hull.size()) - 1;
        while (l < r)
        {
            int m = (l + r) / 2;
            if (dot(hull[m], a, b) < dot(hull[m + 1], a, b)) l = m + 1;
            else r = m; // First maximizing vertex, including edge/zero ties.
        }
        I value = dot(hull[l], a, b);
        if (value < 0) { cout << '-'; value = -value; }
        string digits;
        do { digits += char('0' + value % 10); value /= 10; } while (value);
        reverse(digits.begin(), digits.end());
        cout << digits << ' ' << hull[l].x << ' ' << hull[l].y << '\n';
    }
}
