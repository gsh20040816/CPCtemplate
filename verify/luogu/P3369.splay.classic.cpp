#include "../../src/classic/splay.hpp"
#include <cstdio>
Ordered_Splay<100005> Tree;

int main()
{
    int n;
    scanf("%d", &n);
    Tree.Init();
    while ( n-- )
    {
        int op;
        long long x;
        scanf("%d%lld", &op, &x);
        if ( op == 1 )
            Tree.Insert(x);
        else if ( op == 2 )
            Tree.Erase(x);
        else if ( op == 3 )
            printf("%d\n", Tree.Rank(x));
        else if ( op == 4 )
            printf("%lld\n", Tree.Kth(x));
        else if ( op == 5 )
            printf("%lld\n", *Tree.Predecessor(x));
        else
            printf("%lld\n", *Tree.Successor(x));
    }
    return 0;
}
