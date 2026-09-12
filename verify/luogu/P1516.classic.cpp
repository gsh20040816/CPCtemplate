#include "../../src/classic/linear_congruence.hpp"
#include <cstdio>

int main()
{
    long long x, y, m, n, length;
    scanf("%lld%lld%lld%lld%lld", &x, &y, &m, &n, &length);
    auto [time, period] = Linear_Congruence(m - n, x - y, length);
    if ( time < 0 )
        puts("Impossible");
    else
        printf("%lld\n", time);
    return 0;
}
