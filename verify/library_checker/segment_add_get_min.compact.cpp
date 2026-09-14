#include "../../src/compact/segment_li_chao.hpp"
#include <iostream>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;

    struct Query
    {
        int type;
        long long l, r, a, b;
    };

    vector<Query> ops(n + q);
    vector<long long> xs;
    for (int i = 0; i < n + q; i++)
    {
        auto &o = ops[i];
        o.type = 0;
        if (i >= n) cin >> o.type;
        if (o.type == 0)
            cin >> o.l >> o.r >> o.a >> o.b;
        else
        {
            cin >> o.l;
            xs.push_back(o.l);
        }
    }
    if (xs.empty()) return 0;
    SegmentLiChao t(xs);
    for (auto o : ops)
        if (o.type == 0)
            t.add(o.l, -o.a * o.l - o.b, o.r - 1, -o.a * (o.r - 1) - o.b);
        else
        {
            int id = t.query(o.l);
            if (!id)
                cout << "INFINITY\n";
            else
            {
                auto [num, den] = t.value(id, o.l);
                cout << (long long)(-num / den) << '\n';
            }
        }
}
