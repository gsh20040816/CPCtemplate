#include "../../src/compact/odd_induced_partition.hpp"
#include <iostream>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<pair<int, int>> edges(m);
    for (auto &[u, v] : edges)
    {
        cin >> u >> v;
        u--;
        v--;
    }
    auto color = odd_induced_partition(n, edges);
    if (!color)
        cout << -1 << '\n';
    else
    {
        for (int x : *color) cout << x << ' ';
        cout << '\n';
    }
}
