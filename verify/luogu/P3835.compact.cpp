#include "../../src/compact/persistent_ordered_treap.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    PersistentOrderedTreap tree;
    tree.root.reserve(n + 1);
    tree.t.reserve(26ULL * n + 1);
    for (int i = 1; i <= n; i++)
    {
        int v, op;
        long long x;
        cin >> v >> op >> x;
        if (op == 1)
            tree.insert(v, x);
        else if (op == 2)
            tree.erase(v, x);
        else
        {
            if (op == 3) cout << tree.rank(v, x) << '\n';
            if (op == 4) cout << tree.kth(v, (int)x) << '\n';
            if (op == 5) cout << tree.prev(v, x).value_or(-2147483647LL) << '\n';
            if (op == 6) cout << tree.next(v, x).value_or(2147483647LL) << '\n';
            tree.copy(v);
        }
    }
}
