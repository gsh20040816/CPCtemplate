#include "../../src/compact/maximum_closure.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    std::vector<long long> weight(n + m);
    for (int i = 0; i < n; i++)
    {
        long long cost;
        std::cin >> cost;
        weight[i] = -cost;
    }
    std::vector<std::pair<int, int>> dependencies;
    for (int i = 1; i <= m; i++)
    {
        int u, v;
        long long profit;
        std::cin >> u >> v >> profit;
        weight[n + i - 1] = profit;
        dependencies.push_back({n + i, u});
        dependencies.push_back({n + i, v});
    }
    auto answer = maximum_closure(weight, dependencies);
    std::cout << answer.first << '\n';
}
