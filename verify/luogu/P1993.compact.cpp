#include <bits/stdc++.h>
#include "../../src/compact/spfa.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    Spfa t(n);
    while (m--)
    {
        int op, a, b, c;
        cin >> op >> a >> b;
        if (op != 3) cin >> c;
        if (op == 1) t.add(a, b, -c);
        else if (op == 2) t.add(b, a, c);
        else
        {
            t.add(a, b, 0);
            t.add(b, a, 0);
        }
    }
    cout << (t.run(0) ? "Yes" : "No") << '\n';
}
