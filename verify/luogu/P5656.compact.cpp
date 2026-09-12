#include "../../src/compact/linear_equation.hpp"
#include <cstdio>
#include <numeric>

int main()
{
    int t;
    scanf("%d", &t);
    while (t--)
    {
        long long a, b, c;
        scanf("%lld%lld%lld", &a, &b, &c);
        __int128_t x, y;
        if (!linear_equation(a, b, c, x, y))
        {
            puts("-1");
            continue;
        }
        long long g = gcd(a, b);
        long long dx = b / g;
        long long dy = a / g;
        long long xmin = (x % dx + dx - 1) % dx + 1;
        long long ymin = (y % dy + dy - 1) % dy + 1;
        long long ymax = (c - a * xmin) / b;
        if (ymax <= 0)
        {
            printf("%lld %lld\n", xmin, ymin);
            continue;
        }
        long long count = (ymax - 1) / dy + 1;
        long long xmax = xmin + (count - 1) * dx;
        printf("%lld %lld %lld %lld %lld\n", count, xmin, ymin, xmax, ymax);
    }
    return 0;
}
