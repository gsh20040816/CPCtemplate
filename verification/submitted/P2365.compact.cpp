#include <bits/stdc++.h>
#include <cassert>
using namespace std;
struct MonotoneHull
{
    using ll = long long;
    using I = __int128_t;
    struct Line
    {
        ll m, b;
        int id;

        I value(ll x) const
        {
            return I(m) * x + b;
        }
    };
    vector<Line> q;
    int head = 0;
    ll last_x = 0;
    bool queried = false;

    void add(ll m, ll b, int id)
    {
        assert(q.empty() || m <= q.back().m);
        if (int(q.size()) > head && q.back().m == m)
        {
            if (q.back().b <= b) return;
            q.pop_back();
        }
        Line c{m, b, id};
        while (int(q.size()) - head >= 2)
        {
            auto a = q[q.size() - 2];
            auto b = q.back();
            if ((I(b.b) - a.b) * (b.m - I(c.m)) <
                (I(c.b) - b.b) * (a.m - I(b.m))) break;
            q.pop_back();
        }
        q.push_back(c);
    }

    pair<I, int> query(ll x)
    {
        assert(int(q.size()) > head);
        assert(!queried || last_x <= x);
        queried = true;
        last_x = x;
        while (head + 1 < int(q.size()) && q[head + 1].value(x) < q[head].value(x))
        {
            head++;
        }
        return {q[head].value(x), q[head].id};
    }
};

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    long long s;
    cin >> n >> s;
    vector<long long> t(n + 1), c(n + 1);
    for (int i = 1; i <= n; i++)
    {
        cin >> t[i] >> c[i];
        t[i] += t[i - 1];
        c[i] += c[i - 1];
    }
    MonotoneHull hull;
    hull.add(0, 0, 0);
    long long dp = 0;
    for (int i = 1; i <= n; i++)
    {
        dp = hull.query(t[i] + s).first + t[i] * c[i] + s * c[n];
        hull.add(-c[i], dp, i);
    }
    cout << dp << '\n';
}
