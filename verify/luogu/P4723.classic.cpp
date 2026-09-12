#include "../../src/classic/bostan_mori.hpp"

int main()
{
    unsigned long long n;
    int k;
    scanf("%llu%d", &n, &k);
    using B = Bostan_Mori<>;
    B::Poly c(k), init(k);
    for ( auto &x : c )
    {
        int v;
        scanf("%d", &v);
        x = v;
    }
    for ( auto &x : init )
    {
        int v;
        scanf("%d", &v);
        x = v;
    }
    printf("%d\n", B::Recurrence(init, c, n).v);
}
