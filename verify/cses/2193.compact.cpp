#include "../../src/compact/polygon_area2.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<IntegerPlane::Point> p(n);
    for (auto &a : p) cin >> a.x >> a.y;
    using I = IntegerPlane::I;
    I s = polygon_area2(p), b = 0;
    if (s < 0) s = -s;
    for (int j = 0; j < n; ++j)
    {
        auto a = p[j], c = p[(j + 1) % n];
        b += gcd(abs(a.x - c.x), abs(a.y - c.y));
    }
    auto print = [](I x)
    {
        string s;
        do
        {
            s += char('0' + x % 10);
            x /= 10;
        } while (x);
        reverse(s.begin(), s.end());
        cout << s;
    };
    print((s - b + 2) / 2);
    cout << ' ';
    print(b);
    cout << '\n';
}
