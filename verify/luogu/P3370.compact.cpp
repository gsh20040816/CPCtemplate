#include <bits/stdc++.h>
#include "../../src/compact/string_hash.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    mt19937 rng(random_device{}());
    StringHash::H base;
    for (int j = 0; j < 2; j++)
    {
        base[j] = uniform_int_distribution<int>(257, StringHash::mod[j] - 2)(rng);
    }
    int n;
    cin >> n;
    set<pair<int, StringHash::H>> seen;
    while (n--)
    {
        string s;
        cin >> s;
        StringHash h(s, base);
        seen.insert({int(s.size()), h.get(0, s.size())});
    }
    cout << seen.size() << '\n';
}
