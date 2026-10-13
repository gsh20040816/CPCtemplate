#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_flow6b/main.cpp"

int main(int argc, char **argv)
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string mode = argc > 1 ? argv[1] : "double";
    if (mode == "int")
    {
        Flow<int> g(2);
        g.addEdge(0, 1, 3);
        cout << g.maxFlow(0, 1) << '\n';
        return 0;
    }
    int cases;
    cin >> cases;
    cout << setprecision(17);
    while (cases--)
    {
        int n, m, s, t;
        cin >> n >> m >> s >> t;
        Flow<double> g(n);
        for (int i = 0; i < m; i++)
        {
            int u, v;
            double c;
            cin >> u >> v >> c;
            g.addEdge(u, v, c);
        }
        cout << g.maxFlow(s, t) << '\n';
    }
}
