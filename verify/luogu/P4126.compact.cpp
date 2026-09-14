#include "../../src/compact/mincut_edges.hpp"
#include <iostream>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, s, t;
    cin >> n >> m >> s >> t;
    Dinic g(n);
    while (m--)
    {
        int u, v;
        long long c;
        cin >> u >> v >> c;
        g.add(u, v, c);
    }
    g.flow(s, t);
    for (auto [possible, forced] : mincut_edges(g, s, t))
        cout << possible << ' ' << forced << '\n';
}
