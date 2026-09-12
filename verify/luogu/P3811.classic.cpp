#include "../../src/classic/inverse_table.hpp"
#include <cstdio>

int main()
{
    int n, p;
    scanf("%d%d", &n, &p);
    auto inverse = Inverse_Table(n, p);
    for ( int i = 1; i <= n; i++ )
        printf("%d\n", inverse[i]);
    return 0;
}
