#include "../../src/classic/lucas.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    while ( t-- )
    {
        unsigned long long n, m;
        int p;
        cin >> n >> m >> p;
        static Lucas_Theorem<100000> solver;
        solver.Init(p);
        cout << solver.Choose(n + m, n) << '\n';
    }
    return 0;
}
