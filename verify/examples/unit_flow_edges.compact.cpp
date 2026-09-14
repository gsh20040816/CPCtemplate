#include "../../src/compact/unit_flow_edges.hpp"
#include <iostream>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, s, t, q;
    cin >> n >> m >> s >> t >> q;
    Dinic g(n);
    vector<int> edge(m), ids(q);
    for (int &id : edge)
    {
        int u, v;
        long long cap;
        cin >> u >> v >> cap;
        id = g.add(u, v, cap);
    }
    for (int &id : ids)
    {
        int i;
        cin >> i;
        id = edge[i - 1];
    }
    cout << g.flow(s, t) << '\n';
    for (auto [possible, forced] : unit_flow_edges(g, ids))
        cout << (forced ? 'Y' : possible ? '?' : 'N');
    cout << '\n';
}
