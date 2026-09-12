#include "../../src/compact/euler_lca.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n;
        cin >> n;
        EulerLCA graph(n);
        vector<int> has_parent(n + 1);
        for (int i = 1; i < n; i++)
        {
            int u, v;
            cin >> u >> v;
            graph.add(u, v);
            has_parent[v] = 1;
        }
        int root = 1;
        while (has_parent[root]) root++;
        graph.build(root);
        int u, v;
        cin >> u >> v;
        cout << graph.lca(u, v) << '\n';
    }
    return 0;
}
