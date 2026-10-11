#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN Dominance4D
struct Dominance4D
{
    static vector<int> count(const vector<array<long long, 4>> &p, bool strict = false)
    {
        assert(p.size() <= INT_MAX / 2);
        int n = p.size();
        vector<int> ans(n), bit(n + 1);
        vector<long long> coords;
        for (auto point : p) coords.push_back(point[3]);
        sort(coords.begin(), coords.end());
        coords.erase(unique(coords.begin(), coords.end()), coords.end());
        struct Event
        {
            int id, w;
            bool query;
        };
        vector<Event> events;
        for (int i = 0; i < n; i++)
        {
            int w = lower_bound(coords.begin(), coords.end(), p[i][3]) - coords.begin() + 1;
            events.push_back({i, w, false});
            events.push_back({i, w, true});
        }
        auto less = [&](const Event &a, const Event &b, int axis)
        {
            if (p[a.id][axis] != p[b.id][axis])
                return p[a.id][axis] < p[b.id][axis];
            return strict ? a.query > b.query : a.query < b.query;
        };
        sort(events.begin(), events.end(), [&](const Event &a, const Event &b)
        {
            return less(a, b, 0);
        });
        auto add = [&](int x, int value)
        {
            for (; x <= n; x += x & -x) bit[x] += value;
        };
        auto sum = [&](int x)
        {
            int result = 0;
            for (; x; x -= x & -x) result += bit[x];
            return result;
        };
        auto outer = [&](auto &&self, int l, int r) -> void
        {
            if (r - l <= 1) return;
            int mid = l + (r - l) / 2;
            self(self, l, mid);
            self(self, mid, r);
            vector<Event> a;
            for (int i = l; i < mid; i++)
                if (!events[i].query) a.push_back(events[i]);
            for (int i = mid; i < r; i++)
                if (events[i].query) a.push_back(events[i]);
            sort(a.begin(), a.end(), [&](const Event &u, const Event &v)
            {
                return less(u, v, 1);
            });
            vector<Event> temp(a.size());
            auto inner = [&](auto &&solve, int left, int right) -> void
            {
                if (right - left <= 1) return;
                int middle = left + (right - left) / 2;
                solve(solve, left, middle);
                solve(solve, middle, right);
                int i = left;
                for (int j = middle; j < right; j++)
                {
                    while (i < middle && (strict ? p[a[i].id][2] < p[a[j].id][2]
                                                   : p[a[i].id][2] <= p[a[j].id][2]))
                    {
                        if (!a[i].query) add(a[i].w, 1);
                        i++;
                    }
                    if (a[j].query) ans[a[j].id] += sum(a[j].w - strict);
                }
                for (int j = left; j < i; j++)
                    if (!a[j].query) add(a[j].w, -1);
                merge(a.begin() + left, a.begin() + middle,
                      a.begin() + middle, a.begin() + right, temp.begin() + left,
                      [&](const Event &u, const Event &v)
                      {
                          return p[u.id][2] < p[v.id][2];
                      });
                copy(temp.begin() + left, temp.begin() + right, a.begin() + left);
            };
            inner(inner, 0, a.size());
        };
        outer(outer, 0, events.size());
        if (!strict)
            for (int &value : ans) value--;
        return ans;
    }
};
// END Dominance4D
