#include "../../src/classic/interpolation.hpp"
#include <cstdio>

Lagrange_Interpolation<2000> poly;

int main()
{
    int n;
    long long k;
    scanf("%d%lld", &n, &k);
    std::vector<long long> x(n), y(n);
    for ( int i = 0; i < n; i++ )
        scanf("%lld%lld", &x[i], &y[i]);
    poly.Init(x, y, 998244353);
    printf("%lld\n", poly.Query(k));
}
