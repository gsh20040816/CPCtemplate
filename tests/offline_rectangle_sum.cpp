#include "../src/compact/offline_rectangle_sum.hpp"

int main()
{
    mt19937_64 rng(200000432);
    vector<long long> edge{LLONG_MIN, LLONG_MIN + 1, -1, 0, 1, LLONG_MAX - 1, LLONG_MAX};
    long long checked = 0;
    for (int trial = 0; trial < 2000; trial++)
    {
        int n = rng() % 60;
        int q = rng() % 100;
        vector<array<long long, 3>> points(n);
        vector<array<long long, 4>> queries(q);
        for (auto &p : points)
            p = {edge[rng() % edge.size()], edge[rng() % edge.size()], (long long)(rng() % 2001) - 1000};
        vector<long long> expected(q);
        for (int i = 0; i < q; i++)
        {
            auto &a = queries[i];
            a = {edge[rng() % edge.size()], edge[rng() % edge.size()], edge[rng() % edge.size()], edge[rng() % edge.size()]};
            if (a[0] > a[2])
                swap(a[0], a[2]);
            if (a[1] > a[3])
                swap(a[1], a[3]);
            for (auto [x, y, w] : points)
            {
                if (a[0] <= x && x < a[2] && a[1] <= y && y < a[3])
                    expected[i] += w;
            }
        }
        auto original = points;
        assert(offline_rectangle_sum(points, queries) == expected);
        assert(offline_rectangle_sum(points, queries) == expected);
        assert(original == points);
        checked += q;
    }
    assert(offline_rectangle_sum({{0, 0, LLONG_MAX}}, {{0, 0, 1, 1}})[0] == LLONG_MAX);
    cout << checked << " signed extreme-coordinate scan checks PASS\n";
}
