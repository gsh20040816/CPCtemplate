#include "../../src/compact/ordered_set.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, id = 0;
    cin >> n;
    ost<pair<int, int>> s;
    while (n--)
    {
        int op, x;
        cin >> op >> x;
        if (op == 1) s.insert({x, ++id});
        if (op == 2)
        {
            auto it = s.lower_bound({x, 0});
            if (it != s.end() && it->first == x) s.erase(it);
        }
        if (op == 3) cout << s.order_of_key({x, 0}) + 1 << '\n';
        if (op == 4) cout << s.find_by_order(x - 1)->first << '\n';
        if (op == 5) cout << prev(s.lower_bound({x, 0}))->first << '\n';
        if (op == 6) cout << s.upper_bound({x, INT_MAX})->first << '\n';
    }
}
