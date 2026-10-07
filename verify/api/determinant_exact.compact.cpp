#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
#include "../../src/compact/determinant_exact.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using Z = boost::multiprecision::cpp_int;
    int t;
    cin >> t;
    while (t--)
    {
        int n;
        cin >> n;
        vector<vector<Z>> a(n, vector<Z>(n));
        for (auto &row : a)
            for (auto &x : row)
                cin >> x;
        cout << determinant_exact(move(a)) << '\n';
    }
    return 0;
}
