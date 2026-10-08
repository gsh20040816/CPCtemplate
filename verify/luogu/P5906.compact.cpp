#include <bits/stdc++.h>
#include "../../src/compact/rollback_mo.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<int> a(n), values;
    for (int &x : a) cin >> x;
    values = a;
    sort(values.begin(), values.end());
    values.erase(unique(values.begin(), values.end()), values.end());
    for (int &x : a)
    {
        x = lower_bound(values.begin(), values.end(), x) - values.begin();
    }
    int m;
    cin >> m;
    RollbackMo mo(n);
    for (int i = 0; i < m; i++)
    {
        int l, r;
        cin >> l >> r;
        mo.add(l - 1, r);
    }
    struct Change
    {
        int color, first, last, best;
    };
    vector<Change> history;
    vector<int> first(values.size(), n), last(values.size(), -1), answer(m);
    int best = 0;
    auto add = [&](int i)
    {
        int c = a[i];
        history.push_back({c, first[c], last[c], best});
        first[c] = min(first[c], i);
        last[c] = max(last[c], i);
        best = max(best, last[c] - first[c]);
    };
    auto snapshot = [&]()
    {
        return history.size();
    };
    auto rollback = [&](size_t saved)
    {
        while (history.size() > saved)
        {
            auto h = history.back();
            history.pop_back();
            first[h.color] = h.first;
            last[h.color] = h.last;
            best = h.best;
        }
    };
    mo.run(add, snapshot, rollback, [&](int id)
    {
        answer[id] = best;
    });
    for (int x : answer) cout << x << '\n';
}
