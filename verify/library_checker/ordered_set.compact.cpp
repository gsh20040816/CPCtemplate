// https://judge.yosupo.jp/problem/ordered_set
#include "../../src/compact/ordered_set.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q, x;
    cin >> n >> q;
    ost<int> s;
    while (n--)
    {
        cin >> x;
        s.insert(x);
    }
    while (q--)
    {
        int op;
        cin >> op >> x;
        if (op == 0) s.insert(x);
        if (op == 1) s.erase(x);
        if (op == 2)
        {
            auto it = s.find_by_order(x - 1);
            cout << (it == s.end() ? -1 : *it) << '\n';
        }
        if (op == 3) cout << s.order_of_key(x) + (s.find(x) != s.end()) << '\n';
        if (op == 4)
        {
            auto it = s.upper_bound(x);
            cout << (it == s.begin() ? -1 : *--it) << '\n';
        }
        if (op == 5)
        {
            auto it = s.lower_bound(x);
            cout << (it == s.end() ? -1 : *it) << '\n';
        }
    }
}
