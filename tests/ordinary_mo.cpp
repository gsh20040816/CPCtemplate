#include "../src/compact/ordinary_mo.hpp"

int main()
{
    mt19937 rng(20261012);
    int checked = 0;
    for (int rep = 0; rep < 1200; rep++)
    {
        int n = rng() % 65;
        Mo mo(n);
        vector<pair<int, int>> ranges;
        int q = rep % 7 ? 80 : 0;
        for (int i = 0; i < q; i++)
        {
            int l = rng() % (n + 1);
            int r = rng() % (n + 1);
            if (l > r) swap(l, r);
            if (mo.add(l, r) != i) abort();
            ranges.push_back({l, r});
        }
        for (int block : {0, 1, 7, 100})
        {
            vector<int> active(n);
            vector<int> calls(q);
            auto add = [&](int i)
            {
                if (i < 0 || i >= n || active[i]) abort();
                active[i] = 1;
            };
            auto del = [&](int i)
            {
                if (i < 0 || i >= n || !active[i]) abort();
                active[i] = 0;
            };
            auto answer = [&](int id)
            {
                if (id < 0 || id >= q || calls[id]++) abort();
                auto [l, r] = ranges[id];
                for (int i = 0; i < n; i++)
                    if (active[i] != (l <= i && i < r)) abort();
            };
            mo.run(add, del, answer, block);
            for (int x : calls)
                if (x != 1) abort();
            for (int x : active)
                if (x != 0) abort();
            checked++;
        }
    }
    cout << checked << " full active-set and cleanup checks PASS\n";
}
