#include <bits/stdc++.h>
#include "../../src/compact/exact_cover.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<vector<int>> rows(n);
    for (int i = 0; i < n; i++)
        for (int j = 0, x; j < m; j++)
        {
            cin >> x;
            if (x) rows[i].push_back(j);
        }
    ExactCover dlx(m, rows);
    auto ans = dlx.solve();
    if (!ans) cout << "No Solution!\n";
    else
    {
        for (int i : *ans) cout << i + 1 << ' ';
        cout << '\n';
    }
}
