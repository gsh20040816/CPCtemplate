// Custom API protocol; not an online-judge problem or an official sample.
#include "../../src/compact/gcd_sequence.hpp"
#include <iostream>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    if (!(cin >> n >> q)) return 0;
    vector<pair<GcdSequenceTreap::U, int>> a(n);
    for (auto &[v, t] : a) cin >> v >> t;
    GcdSequenceTreap tr;
    tr.build(a);
    while (q--)
    {
        char op;
        int k, l, r, t;
        GcdSequenceTreap::U v;
        cin >> op;
        if (op == 'I')
        {
            cin >> k >> v >> t;
            tr.insert(k, v, t);
        }
        else if (op == 'E')
        {
            cin >> l >> r;
            tr.erase(l, r);
        }
        else if (op == 'S')
        {
            cin >> k >> v;
            tr.set(k, v);
        }
        else if (op == 'T')
        {
            cin >> k;
            tr.toggle(k);
        }
        else if (op == 'Q')
        {
            cin >> l >> r >> t;
            auto ans = tr.query(l, r, t);
            if (ans) cout << *ans << '\n';
            else cout << "NONE\n";
        }
    }
}
