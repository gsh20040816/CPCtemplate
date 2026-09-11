#include "../../src/classic/algebra.hpp"
#include <cstdio>

int main()
{
    long long a, p, b;
    while ( scanf("%lld%lld%lld", &a, &p, &b) == 3 )
    {
        if ( a == 0 && p == 0 && b == 0 )
            break;
        long long answer = Discrete_Log::Solve(a, b, p);
        if ( answer == -1 )
            printf("No Solution\n");
        else
            printf("%lld\n", answer);
    }
}
