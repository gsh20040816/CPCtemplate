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
    int answer = 0;
    for ( int i = 0; i < (int)s.size(); i++ )
    {
        char ch = 'a' + (s[i] - 'a' + answer) % 26;
        int u = pam.Insert(ch);
        answer = pam.t[u].suffixes;
        std::cout << answer << (i + 1 == (int)s.size() ? '\n' : ' ');
    }
}
