#include "../src/compact/manhattan_order.hpp"

int main()
{
    using I = __int128;
    using P = ManhattanMST::Point;
    mt19937 rng(8702);
    auto dist = [](P a, P b) -> I
    {
        I x = I(a.first) - b.first;
        I y = I(a.second) - b.second;
        return (x < 0 ? -x : x) + (y < 0 ? -y : y);
    };
    auto check = [&](const vector<P> &p, bool oracle)
    {
        auto before = p;
        auto ord = manhattan_order(p);
        if (p != before || ord.size() != p.size())
            abort();
        vector<int> seen(p.size());
        I route = 0;
        for (int i = 0; i < int(ord.size()); i++)
        {
            int u = ord[i];
            if (u < 0 || u >= int(p.size()) || seen[u]++)
                abort();
            if (i)
                route += dist(p[ord[i - 1]], p[u]);
        }
        if (p.empty())
            return;
        if (ord[0] != 0)
            abort();
        I mst = 0;
        if (oracle)
        {
            vector<I> d(p.size(), I(1) << 100);
            fill(seen.begin(), seen.end(), 0);
            d[0] = 0;
            for (int i = 0; i < int(p.size()); i++)
            {
                int u = -1;
                for (int j = 0; j < int(p.size()); j++)
                {
                    if (!seen[j] && (u < 0 || d[j] < d[u]))
                        u = j;
                }
                mst += d[u];
                seen[u] = 1;
                for (int j = 0; j < int(p.size()); j++)
                    d[j] = min(d[j], dist(p[u], p[j]));
            }
        }
        else
            mst = ManhattanMST::solve(p).weight;
        if (route > 2 * mst)
            abort();
    };
    check({}, true);
    check({{LLONG_MIN, LLONG_MIN}, {LLONG_MAX, LLONG_MAX}, {0, 0}}, true);
    for (int it = 0; it < 3000; it++)
    {
        vector<P> p(rng() % 35);
        for (auto &[x, y] : p)
        {
            x = int(rng() % 21) - 10;
            y = int(rng() % 21) - 10;
        }
        check(p, true);
    }
    vector<P> p(50000);
    for (int i = 0; i < int(p.size()); i++)
        p[i] = {i, i};
    check(p, false);
    fill(p.begin(), p.end(), P{0, 0});
    check(p, false);
    cout << "3004 route/permutation/input checks PASS\n";
}
