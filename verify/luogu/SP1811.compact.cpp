#include <iostream>
#include "../../src/compact/string.hpp"
#include "../../src/compact/sam_queries.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s, t;
    getline(cin, s);
    getline(cin, t);
    if (!s.empty() && s.back() == '\r') s.pop_back();
    if (!t.empty() && t.back() == '\r') t.pop_back();
    SuffixAutomaton sam;
    for (char c : s) sam.extend(c - 'a');
    cout << sam_lcs(sam, t).second << '\n';
}
