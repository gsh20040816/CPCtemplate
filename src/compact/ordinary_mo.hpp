#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

struct Mo
{
    struct Query
    {
        int l, r, id;
    };
    int n;
    vector<Query> q;

    Mo(int n) : n(n)
    {
        assert(n >= 0);
    }
    int add(int l, int r)
    {
        assert(0 <= l && l <= r && r <= n);
        int id = q.size();
        q.push_back({l, r, id});
        return id;
    }
    template <class Add, class Del, class Ans>
    void run(Add add, Del del, Ans ans, int block = 0) const
    {
        if (q.empty()) return;
        if (block == 0) block = max(1, int(n / sqrt(double(q.size()))));
        assert(block > 0);
        auto ord = q;
        sort(ord.begin(), ord.end(), [&](const Query &a, const Query &b)
        {
            int x = a.l / block;
            int y = b.l / block;
            if (x != y) return x < y;
            return x & 1 ? a.r > b.r : a.r < b.r;
        });
        int l = 0;
        int r = 0;
        for (auto a : ord)
        {
            while (l > a.l) add(--l);
            while (r < a.r) add(r++);
            while (l < a.l) del(l++);
            while (r > a.r) del(--r);
            ans(a.id);
        }
        while (l < r) del(l++);
    }
};
