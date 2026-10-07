// API example: source-model protocol, not an official HDU statement verification.
#include "../../src/compact/tree_market.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    while (cin >> n)
    {
        TreeMarket tree(n);
        for (int i = 1; i < n; i++)
        {
            int u, v;
            long long w;
            cin >> u >> v >> w;
            tree.add(u - 1, v - 1, w);
        }
        vector<int> existing(n);
        for (int &x : existing) cin >> x;
        auto answer = tree.solve(existing);
        cout << *max_element(answer.begin(), answer.end()) << '\n';
    }
}
