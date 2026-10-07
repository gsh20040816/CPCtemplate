#include "../../src/compact/independent_set.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<vector<int>> id(n + 1, vector<int>(n + 1));
    while (m--)
    {
        int x, y;
        cin >> x >> y;
        id[x][y] = -1;
    }
    int l = 0, r = 0;
    for (int x = 1; x <= n; x++)
        for (int y = 1; y <= n; y++)
            if (id[x][y] != -1)
                id[x][y] = (x + y) % 2 ? ++l : ++r;
    BipartiteMatching g(l, r);
    vector<pair<int, int>> moves = {
        {1, 2}, {1, -2}, {-1, 2}, {-1, -2},
        {2, 1}, {2, -1}, {-2, 1}, {-2, -1}
    };
    for (int x = 1; x <= n; x++)
        for (int y = 1; y <= n; y++)
            if ((x + y) % 2 && id[x][y] != -1)
                for (auto [dx, dy] : moves)
                {
                    int u = x + dx, v = y + dy;
                    if (1 <= u && u <= n && 1 <= v && v <= n && id[u][v] != -1)
                        g.add(id[x][y], id[u][v]);
                }
    auto [a, b] = independent_set(g);
    cout << a.size() + b.size() << '\n';
}
