#include <iostream>
#include "../../src/compact/merge_split_tree.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    MergeSplitTree seg(a);
    for (int i = 0; i < m; i++)
    {
        int op, p;
        cin >> op >> p;
        p--;
        if (op == 0 || op == 3)
        {
            int x, y;
            cin >> x >> y;
            if (op == 0)
                seg.split(p, x - 1, y);
            else
                cout << seg.sum(p, x - 1, y) << '\n';
        }
        else if (op == 1)
        {
            int t;
            cin >> t;
            seg.merge(p, t - 1);
        }
        else if (op == 2)
        {
            long long x;
            int q;
            cin >> x >> q;
            seg.add(p, q - 1, x);
        }
        else
        {
            long long k;
            cin >> k;
            int x = seg.kth(p, k);
            cout << (x == -1 ? -1 : x + 1) << '\n';
        }
    }
}
