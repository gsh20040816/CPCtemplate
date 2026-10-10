#include <iostream>
#include "../../src/compact/shortest_walks.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    StrictSecondShortest solver(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        solver.add(u, v, w);
        solver.add(v, u, w);
    }
    cout << solver.run(1)[n][1] << '\n';
}
