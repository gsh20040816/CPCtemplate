#include "../../src/classic/dynamic_tree.hpp"
#include <cstdio>
Link_Cut_Tree<100005> Tree;

int main()
{
    int n, m;
    scanf("%d%d", &n, &m);
    Tree.Init(n);
    for ( int i = 1; i <= n; i++ )
    {
        unsigned long long x;
        scanf("%llu", &x);
        Tree.Set(i, x);
    }
    while ( m-- )
    {
        int op, x, y;
        scanf("%d%d%d", &op, &x, &y);
        if ( op == 0 )
            printf("%llu\n", Tree.Query(x, y));
        else if ( op == 1 )
            Tree.Link(x, y);
        else if ( op == 2 )
            Tree.Cut(x, y);
        else
            Tree.Set(x, y);
    }
    return 0;
}
