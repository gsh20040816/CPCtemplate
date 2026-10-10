#include <bits/stdc++.h>
using namespace std;

int main()
{
    int n;
    cin >> n;
    long long best = LLONG_MIN, ending = 0;
    for (int i = 0; i < n; i++)
    {
        long long x;
        cin >> x;
        ending = max(x, ending + x);
        best = max(best, ending);
    }
    cout << best << '\n';
}
