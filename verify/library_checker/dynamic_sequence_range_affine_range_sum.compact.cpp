#include <bits/stdc++.h>
#include "../../src/compact/affine_sequence.hpp"
using namespace std;

// BEGIN USAGE
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    AffineSequenceTreap<> t;
    t.a.reserve(n + q + 1);
    for (int i = 0, x; i < n; i++)
    {
        cin >> x;
        t.insert(i, x);
    }
    while (q--)
    {
        int op, l, r, b, c;
        cin >> op >> l;
        if (op == 0)
        {
            cin >> b;
            t.insert(l, b);
        }
        else if (op == 1)
            t.erase(l + 1, l + 1);
        else
        {
            cin >> r;
            if (op == 2)
                t.reverse(l + 1, r);
            else if (op == 3)
            {
                cin >> b >> c;
                t.affine(l + 1, r, b, c);
            }
            else
                cout << t.query(l + 1, r).v << '\n';
        }
    }
}
// END USAGE
