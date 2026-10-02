#include "../../src/compact/mod_inverse.hpp"
#include <cstdio>

int main()
{
    long long a, b;
    scanf("%lld%lld", &a, &b);
    printf("%lld\n", mod_inverse(a, b));
    return 0;
}
