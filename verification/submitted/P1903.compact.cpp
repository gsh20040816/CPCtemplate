#include <cstdio>
#include <array>
#include <algorithm>
#include <cassert>
#include <cmath>
#include <vector>
using namespace std;

struct ModifiedMo
{
    struct Query
    {
        int l, r, t, id;
    };

    int n, m;
    vector<Query> q;

    ModifiedMo(int n, int m) : n(n), m(m)
    {
        assert(n > 0 && m >= 0);
    }

    int add(int l, int r, int t)
    {
        assert(0 <= l && l <= r && r <= n);
        assert(0 <= t && t <= m);
        int id = q.size();
        q.push_back({l, r, t, id});
        return id;
    }

    template <class Add, class Del, class Chg, class Ans>
    void run(Add add, Del del, Chg chg, Ans ans, int block = 0) const
    {
        if (q.empty())
            return;
        if (block == 0)
            block = max(1, int(pow(n, 2.0 / 3)));
        assert(block > 0);
        auto ord = q;
        auto cmp = [&](const Query &a, const Query &b)
        {
            int x = a.l / block, y = b.l / block;
            if (x != y)
                return x < y;
            int p = a.r / block, q = b.r / block;
            if (p != q)
                return (x & 1) ? p > q : p < q;
            return ((x ^ p) & 1) ? a.t > b.t : a.t < b.t;
        };
        sort(ord.begin(), ord.end(), cmp);
        int l = 0, r = 0, t = 0;
        for (auto q : ord)
        {
            while (t < q.t)
            {
                chg(t, true, l, r);
                t++;
            }
            while (t > q.t)
            {
                t--;
                chg(t, false, l, r);
            }
            while (l > q.l)
                add(--l);
            while (r < q.r)
                add(r++);
            while (l < q.l)
                del(l++);
            while (r > q.r)
                del(--r);
            ans(q.id);
        }
    }
};


int main()
{
    int n, m;
    scanf("%d%d", &n, &m);
    vector<int> a(n);
    for (int &v : a)
        scanf("%d", &v);
    vector<int> cur = a;
    vector<array<int, 3>> upd;
    vector<array<int, 3>> qry;
    for (int i = 0; i < m; i++)
    {
        char op;
        int x, y;
        scanf(" %c%d%d", &op, &x, &y);
        x--;
        if (op == 'Q')
            qry.push_back({x, y, int(upd.size())});
        else
        {
            upd.push_back({x, cur[x], y});
            cur[x] = y;
        }
    }
    ModifiedMo mo(n, upd.size());
    for (auto [l, r, t] : qry)
        mo.add(l, r, t);
    vector<int> cnt(1000001), res(qry.size());
    int tot = 0;
    auto add = [&](int p)
    {
        if (cnt[a[p]]++ == 0)
            tot++;
    };
    auto del = [&](int p)
    {
        if (--cnt[a[p]] == 0)
            tot--;
    };
    auto chg = [&](int t, bool fwd, int l, int r)
    {
        auto [p, pre, nxt] = upd[t];
        bool in = l <= p && p < r;
        if (in)
            del(p);
        a[p] = fwd ? nxt : pre;
        if (in)
            add(p);
    };
    auto ans = [&](int id)
    {
        res[id] = tot;
    };
    mo.run(add, del, chg, ans);
    for (int v : res)
        printf("%d\n", v);
}
