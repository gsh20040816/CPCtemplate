#include <bits/stdc++.h>
#include "../../src/compact/gauss_xor.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    while (t--)
    {
        int n;
        cin >> n;
        int m = n * n;
        vector<string> a(m, string(m + 1, '0'));
        vector<pair<int, int>> dir{{0, 0}, {0, 1}, {0, -1}, {1, 0}, {-1, 0}};
        for (int i = 0; i < n; i++)
        {
            string s;
            cin >> s;
            for (int j = 0; j < n; j++)
            {
                int id = i * n + j;
                a[id][m] = s[j] == 'w' ? '1' : '0';
                for (auto [di, dj] : dir)
                {
                    int u = i + di, v = j + dj;
                    if (0 <= u && u < n && 0 <= v && v < n) a[id][u * n + v] = '1';
                }
            }
        }
        auto sol = GaussXor::solve(a, m);
        if (!sol.consistent)
        {
            cout << "inf\n";
            continue;
        }
        string x = sol.particular;
        int ans = m;
        function<void(int)> dfs = [&](int k)
        {
            if (k == (int)sol.kernel.size())
            {
                ans = min(ans, (int)count(x.begin(), x.end(), '1'));
                return;
            }
            dfs(k + 1);
            for (int j = 0; j < m; j++) x[j] ^= sol.kernel[k][j] - '0';
            dfs(k + 1);
            for (int j = 0; j < m; j++) x[j] ^= sol.kernel[k][j] - '0';
        };
        dfs(0);
        cout << ans << '\n';
    }
}
