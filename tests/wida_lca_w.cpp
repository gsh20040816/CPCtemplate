#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_lca_w/main.cpp"

static pair<int, int> brute(const vector<int> &fa, const vector<int> &w, int x, int y)
{
    vector<int> px, py;
    for (int v = x; v; v = fa[v]) px.push_back(v);
    for (int v = y; v; v = fa[v]) py.push_back(v);
    int i = (int)px.size() - 1, j = (int)py.size() - 1, meet = px[i];
    while (i >= 0 && j >= 0 && px[i] == py[j]) {
        meet = px[i];
        i--;
        j--;
    }
    int mx = 0;
    for (int a = x; a != meet; a = fa[a]) mx = max(mx, w[a]);
    for (int a = y; a != meet; a = fa[a]) mx = max(mx, w[a]);
    return {i + 1 + j + 1, mx};
}

int main()
{
    struct Item { int n, root; vector<tuple<int, int, int>> edges; };
    vector<Item> trees = {
        {1, 1, {}},
        {2, 1, {{1, 2, 5}}},
        {4, 1, {{1, 2, 3}, {2, 3, 9}, {3, 4, 4}}},
        {5, 1, {{1, 2, 8}, {1, 3, 1}, {3, 4, 6}, {3, 5, 2}}},
    };
    for (auto [n, root, edges] : trees) {
        Tree t(n);
        vector<vector<pair<int, int>>> g(n + 1);
        for (auto [x, y, w] : edges) {
            t.add(x, y, w);
            g[x].push_back({y, w});
            g[y].push_back({x, w});
        }
        vector<int> fa(n + 1), ew(n + 1), seen(n + 1), st = {root};
        seen[root] = 1;
        for (int i = 0; i < (int)st.size(); i++)
            for (auto [y, w] : g[st[i]]) if (!seen[y]) {
                seen[y] = 1;
                fa[y] = st[i];
                ew[y] = w;
                st.push_back(y);
            }
        t.work(root);
        for (int x = 1; x <= n; x++) for (int y = 1; y <= n; y++) {
            auto [edges, mx] = brute(fa, ew, x, y);
            if (t.clac(x, y) != edges || t.query(x, y) != mx) {
                cout << "bad " << x << ' ' << y << ' ' << t.clac(x, y) << ' ' << edges << ' ' << t.query(x, y) << ' ' << mx << '\n';
                return 1;
            }
        }
    }
    Tree neg(2);
    neg.add(1, 2, -5);
    neg.work(1);
    cout << neg.clac(1, 2) << ' ' << neg.query(1, 2) << '\n';
}
