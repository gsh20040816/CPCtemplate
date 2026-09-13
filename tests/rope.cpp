#include "../src/compact/rope.hpp"

int main()
{
    mt19937 rng(41861);
    vector<rp<int>> s(1);
    vector<vector<int>> a(1);
    for (int t = 0; t < 12000; t++)
    {
        int old = rng() % s.size();
        s.push_back(s[old]);
        a.push_back(a[old]);
        auto &r = s.back();
        auto &v = a.back();
        int op = rng() % 5, p = rng() % (v.size() + 1), x = rng();
        if (op == 0)
        {
            r.insert(p, x);
            v.insert(v.begin() + p, x);
        }
        if (op == 1 && !v.empty())
        {
            p %= v.size();
            r.replace(p, x);
            v[p] = x;
        }
        if (op == 2)
        {
            int len = rng() % (v.size() - p + 1);
            r.erase(p, len);
            v.erase(v.begin() + p, v.begin() + p + len);
        }
        if (op == 3)
        {
            int len = rng() % (v.size() - p + 1);
            r = r.substr(p, len);
            v = vector<int>(v.begin() + p, v.begin() + p + len);
        }
        if (op == 4)
        {
            r.push_back(x);
            v.push_back(x);
        }
        for (int k : {old, (int)s.size() - 1, (int)(rng() % s.size())})
        {
            assert(s[k].size() == a[k].size());
            for (int j = 0; j < int(a[k].size()); j++) assert(s[k][j] == a[k][j]);
        }
    }
    // Large shared trees exercise more than short leaf copies.
    rp<int> base;
    for (int i = 0; i < 200000; i++) base.push_back(i);
    vector<rp<int>> branches(10000, base);
    for (int i = 0; i < 10000; i++)
    {
        branches[i].replace(i, -1);
        assert(base[i] == i);
        assert(branches[i][i] == -1);
        assert(branches[i][i + 1] == i + 1);
    }
    auto slice = base.substr(50000, 100000);
    auto copy = slice;
    slice.erase(0, 50000);
    assert(copy.size() == 100000 && copy[0] == 50000);
    assert(slice.size() == 50000 && slice[0] == 100000);
    cout << "GNU rope branching vector oracle, insert/replace/erase/substr, large "
            "shared copies and version isolation PASS\n";
}
