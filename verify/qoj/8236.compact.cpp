#include <cstdio>
#include <string>
#include "../../src/compact/release_bfs.hpp"

int main()
{
    int n, m, k;
    scanf("%d%d%d", &n, &m, &k);
    vector<int> open(n * m);
    int source = 0;
    for (int i = 0; i < k; i++)
    {
        int x, y;
        scanf("%d%d", &x, &y);
        int u = (x - 1) * m + y - 1;
        if (i == 0)
            source = u;
        else
            open[u] = k - i;
    }
    vector<string> grid(n);
    vector<char> row(m + 1);
    for (auto &s : grid)
    {
        scanf("%s", row.data());
        s = row.data();
    }
    auto dist =
        release_bfs(open,
                    source,
                    [&](int u, auto visit)
                    {
                        int x = u / m, y = u % m;
                        const int dx[] = {-1, 1, 0, 0};
                        const int dy[] = {0, 0, -1, 1};
                        for (int i = 0; i < 4; i++)
                        {
                            int a = x + dx[i], b = y + dy[i];
                            if (a >= 0 && a < n && b >= 0 && b < m && grid[a][b] == '.')
                                visit(a * m + b);
                        }
                    });
    unsigned long long answer = 0;
    for (int d : dist)
        if (d >= 0)
            answer += 1ULL * d * d;
    printf("%llu\n", answer);
}
