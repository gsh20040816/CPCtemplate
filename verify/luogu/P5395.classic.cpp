#include "../../src/classic/stirling.hpp"

int main()
{
    int n;
    scanf("%d", &n);
    auto row = Stirling_Second_Row<167772161>(n, n);
    for ( int i = 0; i <= n; i++ )
        printf("%d%c", row[i].v, i == n ? '\n' : ' ');
}
