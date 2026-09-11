#include "../../src/classic/palindromic_tree.hpp"
#include <iostream>
#include <string>
#include <algorithm>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    std::string s;
    std::cin >> s;
    static Palindromic_Tree<500000> pam;
    pam.Init();
    for ( char ch : s )
        pam.Insert(ch);
    auto count = pam.Occurrences();
    long long answer = 0;
    for ( int u = 2; u < (int)count.size(); u++ )
        answer = std::max(answer, count[u] * pam.t[u].len);
    std::cout << answer << '\n';
}
