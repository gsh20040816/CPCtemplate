// https://judge.yosupo.jp/problem/persistent_queue
#include "../../src/compact/rope.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q;
    cin >> q;
    vector<rp<int>> s(q + 1);
    vector<int> l(q + 1), r(q + 1);
    s[0] = rp<int>(q, 0);
    for (int i = 1; i <= q; i++)
    {
        int op, t, x;
        cin >> op >> t;
        ++t;
        s[i] = s[t];
        l[i] = l[t];
        r[i] = r[t];
        if (op == 0)
        {
            cin >> x;
            s[i].replace(r[i]++, x);
        }
        else
        {
            cout << s[i][l[i]++] << '\n';
        }
    }
}
