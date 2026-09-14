#include "../../src/compact/recurrence.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<int> a(n);
    for (int &x : a) cin >> x;
    auto c = berlekamp_massey(a);
    cout << c.size() << '\n';
    for (int x : c) cout << x << ' ';
    cout << '\n';
}
