#pragma once
#include <algorithm>
#include <cassert>
#include <utility>
#include <vector>
using namespace std;

// BEGIN wqs_independent_set
long long wqs_independent_set(const vector<long long> &a, int k)
{
    using ll = long long;
    assert(k >= 0);
    if (k == 0 || a.empty()) return 0;
    auto solve = [&](ll penalty) -> pair<ll, int>
    {
        pair<ll, int> prev{0, 0}, cur{0, 0};
        for (ll w : a)
        {
            pair<ll, int> take{prev.first + w - penalty, prev.second + 1};
            prev = cur;
            cur = max(cur, take);
        }
        return cur;
    };
    auto free = solve(0);
    if (free.second <= k) return free.first;
    ll lo = 0, hi = max(0LL, *max_element(a.begin(), a.end()));
    while (lo < hi)
    {
        ll mid = lo + (hi - lo + 1) / 2;
        if (solve(mid).second >= k) lo = mid;
        else hi = mid - 1;
    }
    return solve(lo).first + lo * k;
}
// END wqs_independent_set
