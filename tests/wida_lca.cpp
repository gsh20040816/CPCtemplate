#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_lca/main.cpp"

static pair<int, int> brute(const vector<int> &fa, int x, int y)
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
    return {meet, i + 1 + j + 1};
}

int main()
{
    vector<tuple<int, vector<pair<int, int>>, int>> trees = {
        {1, {}, 1},
        {2, {{1, 2}}, 1},
        {4, {{1, 2}, {2, 3}, {3, 4}}, 1},
        {5, {{1, 2}, {1, 3}, {3, 4}, {3, 5}}, 1},
    };
    for (auto [n, edges, root] : trees) {
        Tree t(n);
        vector<int> fa(n + 1);
        for (auto [x, y] : edges) {
            t.add(x, y);
            if (!fa[y]) fa[y] = x;
            else if (!fa[x]) fa[x] = y;
        }
        // Orient toward root with a walk. The cases are rooted at 1 and parents are the smaller endpoint.
        fa.assign(n + 1, 0);
        vector<vector<int>> g(n + 1);
        for (auto [x, y] : edges) {
            g[x].push_back(y);
            g[y].push_back(x);
        }
        vector<int> st = {root};
        vector<int> seen(n + 1);
        seen[root] = 1;
        for (int i = 0; i < (int)st.size(); i++) {
            for (int y : g[st[i]]) if (!seen[y]) {
                seen[y] = 1;
                fa[y] = st[i];
                st.push_back(y);
            }
        }
        t.work(root);
        for (int x = 1; x <= n; x++) for (int y = 1; y <= n; y++) {
            auto [expect, edges] = brute(fa, x, y);
            if (t.lca(x, y) != expect || t.clac(x, y) != edges) {
                cout << "bad " << x << ' ' << y << ' ' << t.lca(x, y) << ' ' << expect << ' ' << t.clac(x, y) << ' ' << edges << '\n';
                return 1;
            }
        }
    }
    cout << "ok\n";
}
