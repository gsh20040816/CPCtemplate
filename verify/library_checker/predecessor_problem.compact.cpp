// https://judge.yosupo.jp/problem/predecessor_problem
#include "../../src/compact/segtree.hpp"

int op(int a, int b)
{
    return a + b;
}

int e()
{
    return 0;
}

bool empty_range(int x)
{
    return x == 0;
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    string t;
    cin >> n >> q >> t;
    vector<int> a(n);
    for (int i = 0; i < n; i++) a[i] = t[i] - '0';
    segtree<int, op, e> s(a);
    while (q--)
    {
        int c, k;
        cin >> c >> k;
        if (c == 0) s.set(k, 1);
        if (c == 1) s.set(k, 0);
        if (c == 2) cout << s.get(k) << '\n';
        if (c == 3)
        {
            int r = s.max_right(k, empty_range);
            cout << (r == n ? -1 : r) << '\n';
        }
        if (c == 4) cout << s.min_left(k + 1, empty_range) - 1 << '\n';
    }
}
