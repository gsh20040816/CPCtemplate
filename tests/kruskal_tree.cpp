#include "../src/compact/kruskal_tree.hpp"
#define CHECK(x) do { if (!(x)) abort(); } while (false)

int main()
{
    mt19937 rng(4768);
    vector<long long> weights{LLONG_MIN, -5, -1, 0, 1, 5, LLONG_MAX};
    for (int it = 0; it < 3000; it++)
    {
        int n = rng() % 10;
        KruskalTree tr(n);
        int m = n ? rng() % 35 : 0;
        for (int i = 0; i < m; i++)
        {
            int u = rng() % n;
            int v = rng() % n;
            CHECK(tr.add(u, v, weights[rng() % weights.size()]) == i);
        }
        for (bool down : {false, true, false})
        {
            int blocks = tr.build(down);
            int k = tr.ch.size();
            CHECK(k == 2 * n - blocks);
            vector<unsigned> mask(k);
            vector<int> parents(k);
            for (int i = 0; i < n; i++)
            {
                CHECK((tr.ch[i] == array<int, 2>{-1, -1}));
                mask[i] = 1u << i;
            }
            for (int i = n; i < k; i++)
            {
                auto [l, r] = tr.ch[i];
                CHECK(0 <= l && l < i && 0 <= r && r < i);
                CHECK(!(mask[l] & mask[r]));
                mask[i] = mask[l] | mask[r];
                parents[l]++;
                parents[r]++;
                CHECK(tr.up[0][l] == i && tr.up[0][r] == i);
            }
            int roots = 0;
            for (int i = 0; i < k; i++)
            {
                CHECK(parents[i] <= 1);
                roots += tr.up[0][i] == -1;
                CHECK((tr.up[0][i] == -1) == (parents[i] == 0));
            }
            CHECK(roots == blocks);
            for (long long w : weights)
            {
                for (bool strict : {false, true})
                {
                    for (int u = 0; u < n; u++)
                    {
                        unsigned want = 1u << u;
                        bool changed = true;
                        while (changed)
                        {
                            unsigned old = want;
                            for (auto e : tr.e)
                            {
                                bool ok = down ? e.w >= w : e.w <= w;
                                if (strict && e.w == w) ok = false;
                                if (ok && (want & ((1u << e.u) | (1u << e.v))))
                                    want |= (1u << e.u) | (1u << e.v);
                            }
                            changed = old != want;
                        }
                        int v = tr.component(u, w, strict);
                        CHECK(mask[v] == want);
                        int p = tr.up[0][v];
                        if (p != -1) CHECK(mask[p] != want);
                    }
                }
            }
        }
        if (n >= 2)
        {
            auto old = tr;
            tr.add(0, n - 1, LLONG_MIN);
            tr.build();
            CHECK(tr.component(0, LLONG_MAX) == tr.component(n - 1, LLONG_MAX));
            CHECK(old.e.size() + 1 == tr.e.size());
            CHECK(old.build() >= tr.build());
        }
    }
    int n = 200000;
    KruskalTree tr(n);
    for (int i = 1; i < n; i++) tr.add(i - 1, i, i);
    CHECK(tr.build() == 1);
    vector<int> cnt(tr.ch.size(), 1);
    for (int u = n; u < (int)tr.ch.size(); u++)
        cnt[u] = cnt[tr.ch[u][0]] + cnt[tr.ch[u][1]];
    for (int i = 0; i < n; i++)
    {
        CHECK(cnt[tr.component(0, i)] == i + 1);
        CHECK(cnt[tr.component(0, i, true)] == max(1, i));
    }
    cout << "3000 forests, thresholds/directions/rebuild/copy, 200000-chain PASS\n";
}
