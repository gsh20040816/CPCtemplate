#include "../../src/compact/color_components.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, root, q;
    cin >> n >> root >> q;
    vector<int> color(n + 1);
    for (int u = 1; u <= n; u++) cin >> color[u];
    HLD h(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        cin >> u >> v;
        h.add(u, v);
    }
    h.build(root);
    ColorComponents tree(h, color);
    while (q--)
    {
        int op, u;
        cin >> op >> u;
        if (op == 0) cout << tree.query(u) << '\n';
        else tree.flip(u);
    }
}
