#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_mcf7b/main.cpp"

int main(int argc, char **argv)
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string mode = argc > 1 ? argv[1] : "cases";
    if (mode == "overflow")
    {
        MinCostFlow<long long> g(3);
        g.addEdge(0, 1, 1, 1);
        g.addEdge(0, 1, 1, 1);
        auto [f, c] = g.flow(0, 1);
        cout << f << ' ' << c << '\n';
        return 0;
    }
    if (mode == "wide")
    {
        MinCostFlow<long long> g(2);
        g.addEdge(0, 1, 3000000000LL, 1);
        auto [f, c] = g.flow(0, 1);
        cout << f << ' ' << c << '\n';
        return 0;
    }
    if (mode == "same")
    {
        MinCostFlow<long long> g(1);
        cout << g.flow(0, 0).first << '\n';
        return 0;
    }
    int cases;
    cin >> cases;
    while (cases--)
    {
        int n, m, s, t;
        cin >> n >> m >> s >> t;
        MinCostFlow<long long> g(n);
        for (int i = 0; i < m; i++)
        {
            int u, v, cap, cost;
            cin >> u >> v >> cap >> cost;
            g.addEdge(u, v, cap, cost);
        }
        auto [f, c] = g.flow(s, t);
        auto restored = g.edges();
        cout << f << ' ' << c << ' ' << restored.size();
        for (auto e : restored)
            cout << ' ' << e.from << ' ' << e.to << ' ' << e.cap << ' ' << e.cost << ' ' << e.flow;
        cout << '\n';
    }
}
