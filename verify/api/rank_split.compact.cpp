#include "../../src/compact/merge_split_tree.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    MergeSplitTree tree(n);
    while (q--)
    {
        int op, s;
        cin >> op >> s;
        if (op == 1)
        {
            int x;
            long long delta;
            cin >> x >> delta;
            tree.add(s, x, delta);
        }
        else if (op == 2)
        {
            long long k;
            bool reverse;
            cin >> k >> reverse;
            cout << tree.split_rank(s, k, reverse) << '\n';
        }
        else if (op == 3)
        {
            int l, r;
            cin >> l >> r;
            cout << tree.sum(s, l, r) << '\n';
        }
        else if (op == 4)
        {
            int other;
            cin >> other;
            tree.merge(s, other);
        }
        else
        {
            long long k;
            cin >> k;
            cout << tree.kth(s, k) << '\n';
        }
    }
}
