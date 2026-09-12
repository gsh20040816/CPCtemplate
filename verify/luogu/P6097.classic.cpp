#include "../../src/classic/subset_convolution.hpp"

int main()
{
    int m;
    scanf("%d", &m);
    int n = 1 << m;
    using F = Set_Convolution<1000000009>;
    F::Poly a(n), b(n);
    for ( auto &x : a )
    {
        int v;
        scanf("%d", &v);
        x = v;
    }
    for ( auto &x : b )
    {
        int v;
        scanf("%d", &v);
        x = v;
    }
    auto c = Subset_Convolution<1000000009>(a, b);
    for ( int s = 0; s < n; s++ )
        printf("%d%c", c[s].v, s + 1 == n ? '\n' : ' ');
}
