#include "../../src/classic/graph.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n;
    while ( std::cin >> n )
    {
        Low_Link graph(n);
        std::vector<std::pair<int, int>> edges;
        for ( int i = 0; i < n; i++ )
        {
            int u, degree;
            char left, right;
            std::cin >> u >> left >> degree >> right;
            while ( degree-- )
            {
                int v;
                std::cin >> v;
                if ( u < v )
                {
                    graph.Insert(u + 1, v + 1);
                    edges.push_back({u, v});
                }
            }
        }
        graph.Run();
        std::vector<std::pair<int, int>> answer;
        for ( int i = 0; i < (int)edges.size(); i++ )
            if ( graph.bridge[i] )
                answer.push_back(edges[i]);
        std::sort(answer.begin(), answer.end());
        std::cout << answer.size() << " critical links\n";
        for ( auto [u, v] : answer )
            std::cout << u << " - " << v << '\n';
        std::cout << '\n';
    }
}
