#include "../../src/compact/graph.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    Lowlink graph(n);
    while (m--)
    {
        int u, v;
        cin >> u >> v;
        graph.add(u, v);
    }
    graph.run();
    vector<int> answer;
    for (int u = 1; u <= n; u++)
        if (graph.cut[u]) answer.push_back(u);
    cout << answer.size() << '\n';
    for (int u : answer) cout << u << ' ';
    cout << '\n';
}
