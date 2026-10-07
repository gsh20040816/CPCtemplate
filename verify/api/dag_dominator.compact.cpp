#include "../../src/compact/dag_dominator.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, root;
    cin >> n >> m >> root;
    DagDominator d(n);
    while (m--)
    {
        int u, v;
        cin >> u >> v;
        d.add(u, v);
    }
    if (!d.build(root))
    {
        cout << -1 << '\n';
        return 0;
    }
    for (int u = 1; u <= n; u++)
        cout << d.idom[u] << (u == n ? '\n' : ' ');
    return 0;
}
