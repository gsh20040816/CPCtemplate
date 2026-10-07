#include <iostream>
#include "../../src/compact/persistent_dsu.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    PersistentDSU d(n);
    for (int i = 1; i <= m; i++)
    {
        int op, x, y;
        cin >> op >> x;
        if (op == 2)
            d.copy(x);
        else
        {
            cin >> y;
            if (op == 1)
                d.merge(i - 1, x - 1, y - 1);
            else
            {
                cout << d.same(i - 1, x - 1, y - 1) << '\n';
                d.copy(i - 1);
            }
        }
    }
}
