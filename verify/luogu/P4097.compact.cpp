#include "../../src/compact/segment_li_chao.hpp"
#include <iostream>
#include <numeric>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    vector<long long> xs(39989);
    iota(xs.begin(), xs.end(), 1);
    SegmentLiChao t(xs);
    int q, last = 0;
    cin >> q;
    while (q--)
    {
        int op, x1, x2;
        long long y1, y2;
        cin >> op >> x1;
        x1 = (x1 + last - 1) % 39989 + 1;
        if (op == 0)
        {
            last = t.query(x1);
            cout << last << '\n';
        }
        else
        {
            cin >> y1 >> x2 >> y2;
            x2 = (x2 + last - 1) % 39989 + 1;
            y1 = (y1 + last - 1) % 1000000000 + 1;
            y2 = (y2 + last - 1) % 1000000000 + 1;
            t.add(x1, y1, x2, y2);
        }
    }
}
