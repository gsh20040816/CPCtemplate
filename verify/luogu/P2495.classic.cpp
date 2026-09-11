#include "../../src/classic/virtual_tree.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n;
    std::cin >> n;
    static Virtual_Tree<250000> tree;
    tree.Init(n);
    for ( int i = 1; i < n; i++ )
    {
        int u, v;
        long long w;
        std::cin >> u >> v >> w;
        tree.Insert(u, v, w);
    }
    tree.Prepare();
    std::vector<int> marked(n + 1);
    std::vector<long long> dp(n + 1);
    int q;
    std::cin >> q;
    while ( q-- )
    {
        int k;
        std::cin >> k;
        std::vector<int> keys(k);
        for ( int &u : keys )
        {
            std::cin >> u;
            marked[u] = 1;
        }
        keys.push_back(1);
        auto result = tree.Build(keys);
        for ( int u : result.vertices )
            dp[u] = 0;
        for ( int i = (int)result.edges.size() - 1; i >= 0; i-- )
        {
            auto e = result.edges[i];
            long long cost = marked[e.to] ? e.minimum : std::min(e.minimum, dp[e.to]);
            dp[e.from] += cost;
        }
        std::cout << dp[1] << '\n';
        for ( int u : keys )
            marked[u] = 0;
    }
}
