#pragma once
#include "data_structure.hpp"

struct OverallKth
{
    using ll = long long;

    struct Event
    {
        int l, r, k, id;
        ll value;
    };

    int n, queries = 0;
    vector<ll> current;
    vector<Event> events;

    OverallKth(const vector<ll> &a) : n(a.size()), current(a)
    {
        assert(n > 0);
        for (int i = 1; i <= n; i++)
        {
            events.push_back({i, 0, 1, -1, a[i - 1]});
        }
    }

    void set(int pos, ll value)
    {
        assert(1 <= pos && pos <= n);
        if (current[pos - 1] == value) return;
        events.push_back({pos, 0, -1, -1, current[pos - 1]});
        events.push_back({pos, 0, 1, -1, value});
        current[pos - 1] = value;
    }

    int query(int l, int r, int k)
    {
        assert(1 <= l && l <= r && r <= n);
        assert(1 <= k && k <= r - l + 1);
        int id = queries++;
        events.push_back({l, r, k, id, 0});
        return id;
    }

    vector<ll> run() const
    {
        vector<ll> answer(queries), values;
        if (queries == 0) return answer;
        auto a = events;
        for (auto e : a)
        {
            if (e.id < 0) values.push_back(e.value);
        }
        sort(values.begin(), values.end());
        values.erase(unique(values.begin(), values.end()), values.end());
        for (auto &e : a)
        {
            if (e.id < 0)
            {
                e.value = lower_bound(values.begin(), values.end(), e.value) - values.begin();
            }
        }
        vector<Event> buffer(a.size());
        vector<bool> left(a.size());
        Fenwick<int> bit(n);
        auto solve = [&](auto &&self, int lo, int hi, int begin, int end) -> void
        {
            if (begin == end) return;
            if (lo == hi)
            {
                for (int i = begin; i < end; i++)
                {
                    if (a[i].id >= 0) answer[a[i].id] = values[lo];
                }
                return;
            }
            int mid = lo + (hi - lo) / 2, count = 0;
            for (int i = begin; i < end; i++)
            {
                auto &e = a[i];
                if (e.id < 0)
                {
                    left[i] = e.value <= mid;
                    if (left[i]) bit.add(e.l, e.k);
                }
                else
                {
                    int smaller = bit.query(e.l, e.r);
                    left[i] = e.k <= smaller;
                    if (!left[i]) e.k -= smaller;
                }
                count += left[i];
            }
            int p = begin, q = begin + count;
            for (int i = begin; i < end; i++)
            {
                auto e = a[i];
                if (e.id < 0 && left[i]) bit.add(e.l, -e.k);
                if (left[i]) buffer[p++] = e;
                else buffer[q++] = e;
            }
            copy(buffer.begin() + begin, buffer.begin() + end, a.begin() + begin);
            self(self, lo, mid, begin, begin + count);
            self(self, mid + 1, hi, begin + count, end);
        };
        solve(solve, 0, int(values.size()) - 1, 0, a.size());
        return answer;
    }
};
