#include "../../src/compact/dominator_tree.hpp"
#include <iostream>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    DominatorTree t(n);
    while (m--)
    {
        int u, v;
        cin >> u >> v;
        t.add(u, v);
    }
    t.build(1);
    vector<int> ans(n + 1);
    for (int i = t.timer; i >= 1; i--)
    {
        int u = t.vertex[i];
        ans[u]++;
        if (u != 1) ans[t.idom[u]] += ans[u];
    }
    for (int u = 1; u <= n; u++) cout << ans[u] << (u == n ? '\n' : ' ');
}
