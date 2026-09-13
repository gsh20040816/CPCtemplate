#include "../../src/compact/gauss_mod.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using A = GaussMod<7>;
    vector<string> days = {"MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"};
    int n, m;
    while (cin >> n >> m && n)
    {
        A::Matrix a(m, vector<A::Z>(n + 1));
        for (int i = 0; i < m; i++)
        {
            int k;
            string start, finish;
            cin >> k >> start >> finish;
            int l = find(days.begin(), days.end(), start) - days.begin();
            int r = find(days.begin(), days.end(), finish) - days.begin();
            a[i][n] = r - l + 1;
            while (k--)
            {
                int x;
                cin >> x;
                a[i][x - 1] = a[i][x - 1] + 1;
            }
        }
        auto answer = A::solve(a, n);
        if (!answer.consistent)
            cout << "Inconsistent data.\n";
        else if (answer.rank < n)
            cout << "Multiple solutions.\n";
        else
        {
            for (int i = 0; i < n; i++)
            {
                int value = answer.particular[i].v;
                if (value < 3) value += 7;
                if (i) cout << ' ';
                cout << value;
            }
            cout << '\n';
        }
    }
    return 0;
}
