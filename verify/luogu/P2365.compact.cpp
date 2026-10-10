#include <iostream>
#include "../../src/compact/monotone_hull.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    long long s;
    cin >> n >> s;
    vector<long long> t(n + 1), c(n + 1);
    for (int i = 1; i <= n; i++)
    {
        cin >> t[i] >> c[i];
        t[i] += t[i - 1];
        c[i] += c[i - 1];
    }
    MonotoneHull hull;
    hull.add(0, 0, 0);
    long long dp = 0;
    for (int i = 1; i <= n; i++)
    {
        dp = hull.query(t[i] + s).first + t[i] * c[i] + s * c[n];
        hull.add(-c[i], dp, i);
    }
    cout << dp << '\n';
}
