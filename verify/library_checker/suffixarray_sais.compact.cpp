// https://judge.yosupo.jp/problem/suffixarray
#include "../../src/compact/sais.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    cin >> s;
    SAIS suffix(s);
    for (int i = 0; i < (int)s.size(); i++)
        cout << suffix.sa[i] << (i + 1 == (int)s.size() ? '\n' : ' ');
}
