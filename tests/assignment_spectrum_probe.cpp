#include <bits/stdc++.h>
#include "../src/compact/assignment_spectrum.hpp"
using namespace std;

void print(__int128_t x)
{
    if (x < 0)
    {
        cout << '-';
        x = -x;
    }
    if (x >= 10)
        print(x / 10);
    cout << char('0' + x % 10);
}

int main()
{
    int t;
    cin >> t;
    while (t--)
    {
        int n, m, e, limit;
        cin >> n >> m >> e >> limit;
        AssignmentSpectrum a(n, m);
        while (e--)
        {
            int x, y;
            long long w;
            cin >> x >> y >> w;
            a.add(x, y, w);
        }
        auto original = a.w;
        int k = a.solve(limit);
        auto best = a.best;
        auto l = a.l;
        auto r = a.r;
        auto lx = a.lx;
        auto ly = a.ly;
        auto level = a.level;
        if (a.solve(limit) != k || a.w != original || a.best != best || a.l != l || a.r != r || a.lx != lx || a.ly != ly || a.level != level)
            return 2;
        cout << k << ' ';
        for (auto value : a.best)
        {
            print(value);
            cout << ' ';
        }
        for (int y : a.l)
            cout << y << ' ';
        for (int x : a.r)
            cout << x << ' ';
        print(a.level);
        cout << ' ';
        for (auto value : a.lx)
        {
            print(value);
            cout << ' ';
        }
        for (auto value : a.ly)
        {
            print(value);
            cout << ' ';
        }
        cout << '\n';
    }
}
