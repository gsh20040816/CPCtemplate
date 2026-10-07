#include "../src/compact/kd_range.hpp"
#include <climits>
#include <iostream>
#include <random>
#include <stdexcept>
#include <tuple>

void require(bool ok)
{
    if (!ok) throw runtime_error("ORACLE_REJECT");
}

using Item = KDRange::Item;
using Point = KDRange::Point;

bool order(Item x, Item y)
{
    return tie(x.p, x.id) < tie(y.p, y.id);
}

void same(vector<Item> x, vector<Item> y)
{
    sort(x.begin(), x.end(), order);
    sort(y.begin(), y.end(), order);
    require(x.size() == y.size());
    for (int i = 0; i < (int)x.size(); i++)
    {
        require(x[i].p == y[i].p && x[i].id == y[i].id);
    }
}

vector<Item> brute(vector<Item> &items, Point low, Point high)
{
    vector<Item> out, keep;
    for (auto v : items)
    {
        if (low[0] <= v.p[0] && v.p[0] <= high[0] &&
            low[1] <= v.p[1] && v.p[1] <= high[1]) out.push_back(v);
        else keep.push_back(v);
    }
    items = keep;
    return out;
}

void audit(KDRange &tree, const vector<Item> &items)
{
    vector<int> seen(tree.a.size());
    seen[0] = 1;
    auto walk = [&](auto &&self, int u, int axis) -> vector<int>
    {
        if (!u) return {};
        require(0 < u && u < (int)seen.size() && !seen[u]);
        seen[u] = 1;
        auto ids = vector<int>{u};
        auto key = [&](int v)
        {
            auto t = tree.a[v].item;
            return tuple(t.p[axis], t.p[axis ^ 1], t.id);
        };
        for (int side = 0; side < 2; side++)
        {
            auto part = self(self, tree.a[u].child[side], axis ^ 1);
            require(4LL * part.size() <= 3LL * tree.a[u].size);
            for (int v : part)
            {
                require(side ? key(v) >= key(u) : key(v) <= key(u));
            }
            ids.insert(ids.end(), part.begin(), part.end());
        }
        auto low = tree.a[u].item.p;
        auto high = low;
        int alive = 0;
        for (int v : ids)
        {
            alive += tree.a[v].present;
            for (int d = 0; d < 2; d++)
            {
                low[d] = min(low[d], tree.a[v].item.p[d]);
                high[d] = max(high[d], tree.a[v].item.p[d]);
            }
        }
        require(tree.a[u].size == (int)ids.size());
        require(tree.a[u].alive == alive);
        require(tree.a[u].low == low && tree.a[u].high == high);
        return ids;
    };
    auto ids = walk(walk, tree.root, 0);
    vector<Item> active;
    for (int u : ids)
    {
        if (tree.a[u].present) active.push_back(tree.a[u].item);
    }
    for (int u : tree.free)
    {
        require(0 < u && u < (int)seen.size() && !seen[u]);
        seen[u] = 1;
    }
    require(count(seen.begin(), seen.end(), 0) == 0);
    require(tree.a[0].size == 0 && tree.a[0].alive == 0);
    require(tree.a[tree.root].size <= 2LL * tree.a[tree.root].alive);
    same(active, items);
}

int main()
{
    try
    {
        mt19937_64 rng(6045270);
        for (int test = 0; test < 100; test++)
        {
            vector<Item> items;
            for (int i = 0; i < test % 30; i++)
            {
                items.push_back({{(long long)(rng() % 11) - 5, (long long)(rng() % 11) - 5}, i % 4});
            }
            KDRange tree(items);
            for (int op = 0; op < 400; op++)
            {
                if (rng() % 3)
                {
                    Item v{{(long long)(rng() % 21) - 10, (long long)(rng() % 21) - 10}, int(rng() % 9)};
                    tree.add(v);
                    items.push_back(v);
                }
                else
                {
                    Point low{(long long)(rng() % 25) - 12, (long long)(rng() % 25) - 12};
                    Point high{(long long)(rng() % 25) - 12, (long long)(rng() % 25) - 12};
                    same(tree.extract(low, high), brute(items, low, high));
                }
                audit(tree, items);
            }
            auto copied = tree;
            tree = KDRange();
            audit(tree, {});
            audit(copied, items);
            same(copied.extract({LLONG_MIN, LLONG_MIN}, {LLONG_MAX, LLONG_MAX}), items);
            audit(copied, {});
        }
        vector<Item> items;
        for (long long x : {LLONG_MIN, -1LL, 0LL, LLONG_MAX})
        {
            for (long long y : {LLONG_MIN, -1LL, 0LL, LLONG_MAX})
            {
                items.push_back({{x, y}, 7});
                items.push_back({{x, y}, 7});
            }
        }
        KDRange edge(items);
        for (auto v : vector<Item>(items))
        {
            same(edge.extract(v.p, v.p), brute(items, v.p, v.p));
            audit(edge, items);
        }
        vector<long long> pos(10000);
        for (int i = 0; i < 10000; i++)
        {
            pos[i] = i;
            items.push_back({{i, 0}, i});
        }
        KDRange moving(items);
        for (int j = 0; j < 50000; j++)
        {
            int id = j % 10000;
            auto out = moving.extract({pos[id], 0}, {pos[id], 0});
            require(out.size() == 1 && out[0].id == id);
            pos[id] = j + 10000;
            moving.add({{pos[id], 0}, id});
            require(moving.a.size() <= 20001);
        }
        items.clear();
        for (int i = 0; i < 10000; i++) items.push_back({{pos[i], 0}, i});
        audit(moving, items);
        for (int repeat = 0; repeat < 10; repeat++)
        {
            auto all = moving.extract({LLONG_MIN, LLONG_MIN}, {LLONG_MAX, LLONG_MAX});
            same(all, items);
            audit(moving, {});
            for (auto v : all) moving.add(v);
            require(moving.a.size() <= 20001);
            audit(moving, items);
        }
        cout << "PASS 40000 random operations, signed64 extremes, 50000 moves, ten full recycle rounds\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
