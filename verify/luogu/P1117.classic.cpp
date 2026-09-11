#include "../../src/classic/suffix_lcp.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int tests;
    std::cin >> tests;
    while ( tests-- )
    {
        std::string s;
        std::cin >> s;
        int n = s.size();
        Suffix_LCP forward{Suffix_Array(s)};
        std::reverse(s.begin(), s.end());
        Suffix_LCP backward{Suffix_Array(s)};
        auto [start, finish] = Square_Counts(forward, backward);
        long long answer = 0;
        for ( int i = 0; i + 1 < n; i++ )
            answer += finish[i] * start[i + 1];
        std::cout << answer << '\n';
    }
}
