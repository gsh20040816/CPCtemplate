#include "../../src/compact/integer_hull.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    auto read = []()
    {
        string s;
        cin >> s;
        bool negative = s[0] == '-';
        int i = negative || s[0] == '+';
        long long value = 0;
        while (i < (int)s.size() && s[i] != '.') value = value * 10 + s[i++] - '0';
        i++;
        for (int j = 0; j < 2; j++)
        {
            value *= 10;
            if (i < (int)s.size()) value += s[i++] - '0';
        }
        return negative ? -value : value;
    };
    int n;
    cin >> n;
    vector<IntegerPlane::Point> p(n);
    for (auto &v : p)
    {
        v.x = read();
        v.y = read();
    }
    auto h = integer_hull(move(p));
    long double length = 0;
    for (int i = 0; i < (int)h.size(); i++)
        length += sqrtl((long double)IntegerPlane::dist2(h[i], h[(i + 1) % h.size()]));
    cout << fixed << setprecision(2) << length / 100 << '\n';
}
