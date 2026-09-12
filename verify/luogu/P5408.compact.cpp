#include "../../src/compact/stirling.hpp"

int main()
{
    int n;
    scanf("%d", &n);
    auto row = stirling_first_row<167772161>(n);
    for (int i = 0; i <= n; i++) printf("%d%c", row[i].v, i == n ? '\n' : ' ');
}
