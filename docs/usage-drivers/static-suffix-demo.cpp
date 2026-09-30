#include "../../src/compact/suffix_lcp.hpp"

// Synthetic API demonstration; not an online-judge problem or submission driver.
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    if (!(cin >> n >> q)) return 0;
    assert(0 <= n && n <= 200000 && 0 <= q && q <= 200000);
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    string s;
    getline(cin, s); // Keep the empty line when n = 0; do not use cin >> ws.
    assert((int)s.size() == n);
    for (char c : s) assert('a' <= c && c <= 'z');
    SuffixLCP forward{SuffixArray(s)};
    string r(s.rbegin(), s.rend());
    SuffixLCP reversed{SuffixArray(r)};
    while (q--)
    {
        int op;
        cin >> op;
        if (op == 0)
        {
            int x, y;
            cin >> x >> y;
            cout << forward.query(x, y) << '\n';
        }
        else if (op == 1)
        {
            int l1, r1, l2, r2;
            cin >> l1 >> r1 >> l2 >> r2;
            cout << forward.compare(l1, r1, l2, r2) << '\n';
        }
        else
        {
            assert(op == 2);
            int x, y;
            cin >> x >> y;
            cout << prefix_lcs(reversed, x, y) << '\n';
        }
    }
}
