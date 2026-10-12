#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// The functional comparators in kuangbin 8.5, with names isolated.
struct SourceHeapCmp
{
    bool operator()(int x, int y)
    {
        return x > y;
    }
};
struct SourceHeapNode
{
    int x, y;
    friend bool operator<(SourceHeapNode a, SourceHeapNode b)
    {
        return a.x > b.x;
    }
};
struct SourceDescending
{
    bool operator()(const int &a, const int &b) const
    {
        return a > b;
    }
};
struct SourceNode
{
    int x, y;
};
struct SourceNodeCmp
{
    bool operator()(const SourceNode &a, const SourceNode &b) const
    {
        if (a.x != b.x)
            return a.x < b.x;
        return a.y > b.y;
    }
};

int main()
{
    mt19937 rng(20261012);
    long long operations = 0;
    for (int trial = 0; trial < 1000; trial++)
    {
        priority_queue<int> hi;
        priority_queue<int, vector<int>, greater<int>> lo;
        priority_queue<int, vector<int>, SourceHeapCmp> custom;
        priority_queue<SourceHeapNode> nodes;
        vector<int> values;
        for (int i = 0; i < trial % 101; i++)
        {
            int x = int(rng() % 21) - 10;
            values.push_back(x);
            hi.push(x);
            lo.push(x);
            custom.push(x);
            nodes.push({x, i});
            assert(hi.size() == values.size());
        }
        sort(values.begin(), values.end());
        for (int i = 0; i < (int)values.size(); i++)
        {
            assert(hi.top() == values[values.size() - 1 - i]);
            assert(lo.top() == values[i]);
            assert(custom.top() == values[i]);
            assert(nodes.top().x == values[i]);
            hi.pop();
            lo.pop();
            custom.pop();
            nodes.pop();
            operations++;
        }
        assert(hi.empty() && lo.empty() && custom.empty() && nodes.empty());
    }
    multiset<int, SourceDescending> s;
    vector<int> values;
    for (int step = 0; step < 20000; step++)
    {
        int x = int(rng() % 31) - 15;
        int op = rng() % 5;
        if (op < 2)
        {
            s.insert(x);
            values.push_back(x);
        }
        else if (op == 2)
        {
            auto it = s.find(x);
            auto jt = find(values.begin(), values.end(), x);
            assert((it == s.end()) == (jt == values.end()));
            if (it != s.end())
            {
                s.erase(it);
                values.erase(jt);
            }
        }
        else if (op == 3)
        {
            int count = std::count(values.begin(), values.end(), x);
            assert(s.erase(x) == count);
            values.erase(remove(values.begin(), values.end(), x), values.end());
        }
        else if (step % 17 == 0)
        {
            s.clear();
            values.clear();
        }
        sort(values.begin(), values.end(), greater<int>());
        assert(vector<int>(s.begin(), s.end()) == values);
        for (int k = -17; k <= 17; k++)
        {
            auto a = s.lower_bound(k);
            auto b = s.upper_bound(k);
            int l = 0, r = 0;
            while (l < (int)values.size() && values[l] > k)
                l++;
            while (r < (int)values.size() && values[r] >= k)
                r++;
            assert(distance(s.begin(), a) == l);
            assert(distance(s.begin(), b) == r);
            assert(s.equal_range(k) == make_pair(a, b));
            assert(s.count(k) == r - l);
        }
        assert(s.size() == values.size() && s.empty() == values.empty());
        operations++;
    }
    multiset<SourceNode, SourceNodeCmp> nodes;
    set<SourceNode, SourceNodeCmp> unique_nodes;
    vector<pair<int, int>> keys;
    for (int i = 0; i < 1000; i++)
    {
        int x = rng() % 21, y = rng() % 21;
        nodes.insert({x, y});
        unique_nodes.insert({x, y});
        keys.push_back({x, -y});
    }
    sort(keys.begin(), keys.end());
    int i = 0;
    for (auto p : nodes)
        assert(make_pair(p.x, -p.y) == keys[i++]);
    keys.erase(unique(keys.begin(), keys.end()), keys.end());
    assert(unique_nodes.size() == keys.size());
    i = 0;
    for (auto p : unique_nodes)
        assert(make_pair(p.x, -p.y) == keys[i++]);
    // Source's warning about also declaring > is not a language restriction.
    struct Both
    {
        int x;
        bool operator<(const Both &b) const
        {
            return x < b.x;
        }
        bool operator>(const Both &b) const
        {
            return x > b.x;
        }
    };
    priority_queue<Both> both;
    both.push({1});
    both.push({2});
    assert(both.top().x == 2);
    cout << operations << " operations; source comparators, bounds, erasure PASS\n";
}
