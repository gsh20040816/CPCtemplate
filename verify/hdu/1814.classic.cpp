#include "../../src/classic/lex_two_sat.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while ( cin >> n >> m )
    {
        static Lex_Two_SAT<10000> graph;
        graph.Init(n);
        while ( m-- )
        {
            int u, v;
            cin >> u >> v;
            int x = (u + 1) / 2;
            int y = (v + 1) / 2;
            bool a = u % 2 == 0;
            bool b = v % 2 == 0;
            graph.Add(x, !a, y, !b);
        }
        if ( !graph.Solve() )
            cout << "NIE\n";
        else
            for ( int x = 1; x <= n; x++ )
                cout << 2 * x - 1 + graph.answer[x] << '\n';
    }
    return 0;
}
