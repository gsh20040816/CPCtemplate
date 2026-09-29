#include "../src/compact/bridge_augmentation.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    while (t--)
    {
        int n, m;
        cin >> n >> m;
        BiconnectedCore graph(n);
        for (int i = 0; i < m; i++)
        {
            int u, v;
            cin >> u >> v;
            graph.add(u, v);
        }
        graph.run();
        auto tree = bridge_component_forest(graph);
        cout << graph.cnt << '\n';
        for (int u = 1; u <= n; u++) cout << graph.bel[u] << ' ';
        cout << '\n';
        for (int u = 1; u <= graph.cnt; u++)
        {
            cout << tree[u].size();
            for (auto [v, id] : tree[u]) cout << ' ' << v << ' ' << id;
            cout << '\n';
        }
        int bridges = count(graph.bridge.begin(), graph.bridge.end(), 1);
        if (graph.cnt - bridges != 1)
        {
            cout << -1 << '\n';
            continue;
        }
        auto added = bridge_augmentation(graph);
        cout << added.size() << '\n';
        for (auto [u, v] : added) cout << u << ' ' << v << '\n';
    }
}
