#include "../../src/classic/chirp_z.hpp"

int main()
{
    int n, m, a, r;
    scanf("%d%d%d%d", &n, &m, &a, &r);
    using Z = Mod_Int<998244353>;
    vector<Z> f(n);
    for ( auto &x : f )
    {
        int v;
        scanf("%d", &v);
        x = v;
    }
    auto answer = Chirp_Z(f, Z(a), Z(r), m);
    for ( int i = 0; i < m; i++ )
        printf("%d%c", answer[i].v, i + 1 == m ? '\n' : ' ');
}
