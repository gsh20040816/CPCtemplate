#pragma once
#include "data_structure.hpp"

// BEGIN offline_rectangle_sum
vector<long long> offline_rectangle_sum(vector<array<long long, 3>> points,
                                       const vector<array<long long, 4>> &queries)
{
    using ll = long long;
    assert(points.size() < (1U << 30) && queries.size() < (1U << 30));
    vector<ll> ys;
    for (auto [x, y, w] : points)
        ys.push_back(y);
    sort(ys.begin(), ys.end());
    ys.erase(unique(ys.begin(), ys.end()), ys.end());
    auto rank = [&](ll y)
    {
        return int(lower_bound(ys.begin(), ys.end(), y) - ys.begin());
    };
    struct Event
    {
        ll x;
        int d, u, id, sign;
    };
    vector<Event> events;
    events.reserve(2 * queries.size());
    for (int i = 0; i < (int)queries.size(); i++)
    {
        auto [l, d, r, u] = queries[i];
        assert(l <= r && d <= u);
        if (l == r || d == u)
            continue;
        events.push_back({l, rank(d), rank(u), i, -1});
        events.push_back({r, rank(d), rank(u), i, 1});
    }
    sort(points.begin(), points.end());
    sort(events.begin(), events.end(), [](const Event &a, const Event &b)
    {
        return a.x < b.x;
    });
    Fenwick<ll> bit(ys.size());
    vector<ll> answer(queries.size());
    int p = 0;
    for (auto e : events)
    {
        while (p < (int)points.size() && points[p][0] < e.x)
        {
            auto [x, y, w] = points[p];
            bit.add(rank(y) + 1, w);
            p++;
        }
        ll sum = bit.sum(e.u) - bit.sum(e.d);
        answer[e.id] += e.sign * sum;
    }
    return answer;
}
// END offline_rectangle_sum
