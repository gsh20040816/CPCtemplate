#include "../../src/compact/sequence_scapegoat.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<long long> a(n);
    for (auto &x : a)
        cin >> x;
    SequenceScapegoat tree(a);
    int q;
    cin >> q;
    int ans = 0;
    while (q--)
    {
        int op, l, r;
        cin >> op >> l >> r;
        l = (l + ans - 1) % n + 1;
        r = (r + ans - 1) % n + 1;
        if (l > r)
            swap(l, r);
        if (op == 1)
            tree.rotate(l, r);
        else
        {
            int k;
            cin >> k;
            k = (k + ans - 1) % n + 1;
            ans = tree.count(l, r, k);
            cout << ans << '\n';
        }
    }
}
