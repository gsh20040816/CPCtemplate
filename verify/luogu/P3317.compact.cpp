#include "../../src/compact/tree_probability.hpp"

int main()
{
    int n;
    cin >> n;
    vector<vector<int>> p(n, vector<int>(n));
    for (auto &row : p)
        for (int &v : row)
        {
            long double x;
            cin >> x;
            v = lroundl(100 * x);
        }
    cout << fixed << setprecision(12) << tree_probability(p) << '\n';
}
