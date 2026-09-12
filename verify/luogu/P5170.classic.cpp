#include "../../src/classic/floor_moments.hpp"
#include <cstdio>

int main()
{
    int t;
    scanf("%d", &t);
    while ( t-- )
    {
        long long n, a, b, c;
        scanf("%lld%lld%lld%lld", &n, &a, &b, &c);
        auto result = Floor_Moments(n + 1, c, a, b);
        printf("%d %d %d\n", result[0].v, result[2].v, result[1].v);
    }
    return 0;
}
