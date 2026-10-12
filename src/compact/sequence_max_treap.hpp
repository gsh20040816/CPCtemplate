#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <random>
#include <utility>
#include <vector>
using namespace std;

struct SequenceMaxTreap
{
    using ll = long long;
    struct Node
    {
        int left = 0, right = 0, size = 0;
        ll value = LLONG_MIN, maximum = LLONG_MIN;
        unsigned long long priority = 0;
    };
    vector<Node> t{Node{}};
    mt19937_64 rng;

    SequenceMaxTreap(unsigned long long seed = 712367821) : rng(seed)
    {
    }

    int size(int root) const
    {
        return t[root].size;
    }

    void pull(int p)
    {
        t[p].size = size(t[p].left) + size(t[p].right) + 1;
        t[p].maximum = max({t[p].value, t[t[p].left].maximum,
                           t[t[p].right].maximum});
    }

    pair<int, int> split(int p, int k)
    {
        assert(0 <= k && k <= size(p));
        if (!p)
            return {0, 0};
        if (k <= size(t[p].left))
        {
            auto [left, right] = split(t[p].left, k);
            t[p].left = right;
            pull(p);
            return {left, p};
        }
        auto [left, right] = split(t[p].right, k - size(t[p].left) - 1);
        t[p].right = left;
        pull(p);
        return {p, right};
    }

    int merge(int left, int right)
    {
        if (!left || !right)
            return left ? left : right;
        if (t[left].priority > t[right].priority)
        {
            t[left].right = merge(t[left].right, right);
            pull(left);
            return left;
        }
        t[right].left = merge(left, t[right].left);
        pull(right);
        return right;
    }

    int insert(int &root, int pos, ll value)
    {
        assert(0 <= pos && pos <= size(root) && t.size() < INT_MAX);
        int id = t.size();
        t.push_back({0, 0, 1, value, value, rng()});
        auto [left, right] = split(root, pos);
        root = merge(merge(left, id), right);
        return id;
    }

    int last_greater(int p, ll value) const
    {
        if (!p || t[p].maximum <= value)
            return -1;
        int right = last_greater(t[p].right, value);
        if (right != -1)
            return size(t[p].left) + 1 + right;
        if (t[p].value > value)
            return size(t[p].left);
        return last_greater(t[p].left, value);
    }

    void collect(int p, vector<int> &order) const
    {
        if (!p)
            return;
        collect(t[p].left, order);
        order.push_back(p);
        collect(t[p].right, order);
    }

    vector<int> ids(int root) const
    {
        vector<int> order;
        collect(root, order);
        return order;
    }
};
