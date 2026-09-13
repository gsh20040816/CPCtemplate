#include "../../src/compact/ordered_set.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, id = 0, last = 0, ans = 0;
    cin >> n >> m;
    ost<pair<int, int>> s;
    while (n--)
    {
        int x;
        cin >> x;
        s.insert({x, ++id});
    }
    while (m--)
    {
        int op, x;
        cin >> op >> x;
        x ^= last;
        if (op == 1) s.insert({x, ++id});
        if (op == 2) s.erase(s.lower_bound({x, 0}));
        if (op == 3) last = s.order_of_key({x, 0}) + 1;
        if (op == 4) last = s.find_by_order(x - 1)->first;
        if (op == 5) last = prev(s.lower_bound({x, 0}))->first;
        if (op == 6) last = s.upper_bound({x, INT_MAX})->first;
        if (op >= 3) ans ^= last;
    }
    cout << ans << '\n';
}
