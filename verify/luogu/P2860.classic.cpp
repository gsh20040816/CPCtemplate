#include "../../src/classic/bridge_augmentation.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    static Biconnected_Graph<5000> graph;
    graph.Init(n);
    for ( int i = 0; i < m; i++ )
    {
        int u, v;
        cin >> u >> v;
        graph.Insert(u, v);
    }
    graph.Run();
    cout << Bridge_Augmentation(graph).size() << '\n';
    return 0;
}
