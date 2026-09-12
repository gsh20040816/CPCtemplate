#include "../../src/compact/graph.hpp"
#include <iostream>
#include <string>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m && (n || m))
    {
        TwoSAT graph(n);
        graph.add(1, true, 1, true);
        while (m--)
        {
            string a, b;
            cin >> a >> b;
            int x = stoi(a.substr(0, a.size() - 1)) + 1;
            int y = stoi(b.substr(0, b.size() - 1)) + 1;
            graph.add(x, a.back() == 'w', y, b.back() == 'w');
        }
        if (!graph.solve())
        {
            cout << "bad luck\n";
            continue;
        }
        for (int i = 1; i < n; i++)
        {
            if (i > 1) cout << ' ';
            cout << i << (graph.ans[i + 1] ? 'w' : 'h');
        }
        cout << '\n';
    }
    return 0;
}
