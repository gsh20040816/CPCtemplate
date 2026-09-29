#include <bits/stdc++.h>
#include "../../src/compact/kd_tree_sum.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, op, last = 0;
    cin >> n;
    KDTreeSum<> s(200000);
    while (cin >> op && op != 3)
    {
        int x, y;
        cin >> x >> y;
        x ^= last;
        y ^= last;
        if (op == 1)
        {
            int value;
            cin >> value;
            value ^= last;
            s.add(x, y, value);
        }
        else
        {
            int x2, y2;
            cin >> x2 >> y2;
            x2 ^= last;
            y2 ^= last;
            last = s.query(x, y, x2, y2);
            cout << last << '\n';
        }
    }
}
