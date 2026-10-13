#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_kim/main.cpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    while (n--)
    {
        int y, m, d;
        cin >> y >> m >> d;
        cout << isLeap(y) << ' ' << daysInMonth(y, m) << ' ' << getDay(y, m, d) << '\n';
    }
}
