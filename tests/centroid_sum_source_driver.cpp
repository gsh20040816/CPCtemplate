// Source-protocol adapter, not an independently verified HDU submission.
#include "../src/compact/centroid_sum.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m)
    {
        vector<long long> a(n);
        for (auto &x : a) cin >> x;
        CentroidSum<long long> tree(n);
        for (int i = 1; i < n; i++)
        {
            int u, v;
            cin >> u >> v;
            tree.add(u - 1, v - 1);
        }
        tree.build(a);
        while (m--)
        {
            char op;
            int u;
            long long x;
            cin >> op >> u >> x;
            if (op == '!') tree.set(u - 1, x);
            else cout << tree.query(u - 1, x) << '\n';
        }
    }
}
