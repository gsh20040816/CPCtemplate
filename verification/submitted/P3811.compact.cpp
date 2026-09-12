#include <cassert>
#include <vector>
using namespace std;

// BEGIN inverse_table
inline vector<int> inverse_table(int n, int p)
{
    assert(p >= 2 && 0 <= n && n < p);
    vector<int> inverse(n + 1);
    if (n)
        inverse[1] = 1;
    for (int i = 2; i <= n; i++)
        inverse[i] = p - 1LL * (p / i) * inverse[p % i] % p;
    return inverse;
}

// END inverse_table

#include <cstdio>

int main()
{
    int n, p;
    scanf("%d%d", &n, &p);
    auto inverse = inverse_table(n, p);
    for (int i = 1; i <= n; i++)
        printf("%d\n", inverse[i]);
    return 0;
}
