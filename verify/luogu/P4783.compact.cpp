#include "../../src/compact/matrix_inverse.hpp"

int main()
{
    using Z = ModInt<1000000007>;
    int n;
    scanf("%d", &n);
    vector<vector<Z>> a(n, vector<Z>(n));
    for (auto &row : a)
        for (auto &x : row)
        {
            int v;
            scanf("%d", &v);
            x = v;
        }
    auto b = matrix_inverse<1000000007>(a);
    if (!b)
        puts("No Solution");
    else
        for (auto &row : *b)
        {
            for (auto x : row) printf("%d ", x.v);
            puts("");
        }
}
