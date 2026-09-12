#include "../../src/compact/linear_congruence.hpp"
#include <cstdio>

int main()
{
    long long x, y, m, n, length;
    scanf("%lld%lld%lld%lld%lld", &x, &y, &m, &n, &length);
    auto [time, period] = linear_congruence(m - n, x - y, length);
    if (time < 0)
        puts("Impossible");
    else
        printf("%lld\n", time);
    return 0;
}
