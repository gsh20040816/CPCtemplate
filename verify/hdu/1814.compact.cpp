#include "../../src/compact/lex_two_sat.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m)
    {
        LexTwoSAT graph(n);
        while (m--)
        {
            int u, v;
            cin >> u >> v;
            int x = (u + 1) / 2;
            int y = (v + 1) / 2;
            bool a = u % 2 == 0;
            bool b = v % 2 == 0;
            graph.add(x, !a, y, !b);
        }
        if (!graph.solve())
            cout << "NIE\n";
        else
            for (int x = 1; x <= n; x++)
                cout << 2 * x - 1 + graph.answer[x] << '\n';
    }
    return 0;
}
