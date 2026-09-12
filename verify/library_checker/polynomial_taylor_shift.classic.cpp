#include "../../src/classic/polynomial_shift.hpp"

int main()
{
    int n, c;
    scanf("%d%d", &n, &c);
    using Z = Mod_Int<998244353>;
    vector<Z> f(n);
    for ( auto &x : f )
    {
        int v;
        scanf("%d", &v);
        x = v;
    }
    auto answer = Polynomial_Shift(f, Z(c));
    for ( int i = 0; i < n; i++ )
        printf("%d%c", answer[i].v, i + 1 == n ? '\n' : ' ');
}
