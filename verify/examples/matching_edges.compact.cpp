#include "../../src/compact/matching_edges.hpp"
#include <iostream>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, k;
    cin >> n >> m >> k;
    vector<pair<int, int>> edges(k);
    for (auto &[u, v] : edges) cin >> u >> v;
    auto [size, labels] = matching_edges(n, m, edges);
    cout << size << '\n';
    for (auto [possible, forced] : labels) cout << possible << ' ' << forced << '\n';
}
