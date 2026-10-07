#include "../../src/compact/independent_set.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, e;
    cin >> n >> m >> e;
    BipartiteMatching g(n, m);
    while (e--)
    {
        int u, v;
        cin >> u >> v;
        g.add(u, v);
    }
    auto [a, b] = independent_set(g);
    cout << a.size() + b.size() << '\n';
    cout << a.size();
    for (int u : a) cout << ' ' << u;
    cout << '\n';
    cout << b.size();
    for (int v : b) cout << ' ' << v;
    cout << '\n';
}
