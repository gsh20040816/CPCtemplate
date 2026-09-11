#include "../../src/classic/treap.hpp"
#include <cstdio>
Sequence_Treap<100005> Tree;

int main()
{
    int n, m;
    scanf("%d%d", &n, &m);
    Tree.Init();
    for ( int i = 1; i <= n; i++ )
        Tree.Insert(i - 1, i);
    while ( m-- )
    {
        int l, r;
        scanf("%d%d", &l, &r);
        Tree.Reverse(l, r);
    }
    for ( long long x : Tree.Values() )
        printf("%lld ", x);
    printf("\n");
    return 0;
}
