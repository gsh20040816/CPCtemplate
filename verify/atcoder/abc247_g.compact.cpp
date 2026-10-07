#include <bits/stdc++.h>
#include "../../src/compact/assignment_spectrum.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    AssignmentSpectrum matching(150, 150);
    while (n--)
    {
        int a, b;
        long long c;
        cin >> a >> b >> c;
        matching.add(a - 1, b - 1, c);
    }
    int k = matching.solve();
    cout << k << '\n';
    for (int i = 1; i <= k; i++)
        cout << (long long)matching.best[i] << '\n';
    return 0;
}
