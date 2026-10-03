#include "../src/compact/linear_equation.hpp"

string decimal(__int128 x)
{
    bool negative = x < 0;
    __uint128_t v = negative ? __uint128_t(-(x + 1)) + 1 : x;
    string s;
    do
    {
        s += char('0' + v % 10);
        v /= 10;
    } while (v);
    if (negative) s += '-';
    reverse(s.begin(), s.end());
    return s;
}

int main()
{
    long long a, b, c;
    while (cin >> a >> b >> c)
    {
        __int128 x, y;
        bool ok = linear_equation(a, b, c, x, y);
        cout << ok << ' ' << decimal(x) << ' ' << decimal(y) << '\n';
    }
}
