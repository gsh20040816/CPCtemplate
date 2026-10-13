#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_twosat/main.cpp"
#include "../src/compact/graph.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int cases;
    cin >> cases;
    while (cases--)
    {
        int n, m;
        cin >> n >> m;
        vector<array<int, 4>> clause(m);
        TwoSat original(n);
        TwoSAT library(n);
        for (int i = 0; i < m; i++)
        {
            int u, f, v, g;
            cin >> u >> f >> v >> g;
            clause[i] = {u, f, v, g};
            original.addClause(u, f, v, g);
            library.add(u + 1, f, v + 1, g);
        }
        bool first = original.satisfiable();
        auto bits = original.answer();
        bool second = original.satisfiable();
        auto again = original.answer();
        bool known = library.solve();
        cout << first << ' ' << second << ' ' << known << ' ' << n;
        for (int i = 0; i < n; i++)
            cout << ' ' << bits[i] << ' ' << again[i];
        cout << '\n';
    }
}
