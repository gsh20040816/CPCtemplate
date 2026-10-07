#include "../src/compact/kd_nearest.hpp"
#include <iostream>
#include <stdexcept>

void require(bool ok)
{
    if (!ok) throw runtime_error("KD invariant");
}

template <int D> void run()
{
    int n, m;
    cin >> n >> m;
    vector<typename KDNearest<D>::Point> p(n);
    for (auto &x : p)
    {
        for (int &v : x) cin >> v;
    }
    KDNearest<D> tree(p);
    require(tree.p == p);
    vector<int> seen(n);
    auto check = [&](auto &&self, int u) -> vector<int>
    {
        if (u == -1) return {};
        require(0 <= u && u < n && !seen[u]);
        seen[u]++;
        vector<int> ids{u};
        int sizes[2]{};
        for (int i = 0; i < 2; i++)
        {
            auto part = self(self, tree.a[u].child[i]);
            sizes[i] = part.size();
            ids.insert(ids.end(), part.begin(), part.end());
        }
        require(abs(sizes[0] - sizes[1]) <= 1);
        require(tree.a[u].first == *min_element(ids.begin(), ids.end()));
        auto low = p[u];
        auto high = p[u];
        for (int id : ids)
        {
            for (int d = 0; d < D; d++)
            {
                low[d] = min(low[d], p[id][d]);
                high[d] = max(high[d], p[id][d]);
            }
        }
        require(low == tree.a[u].low && high == tree.a[u].high);
        return ids;
    };
    require((int)check(check, tree.root).size() == n);
    auto copied = tree;
    tree = KDNearest<D>();
    require(tree.root == -1 && tree.query({}, 0).empty());
    while (m--)
    {
        typename KDNearest<D>::Point q{};
        for (int &v : q) cin >> v;
        int k, far;
        cin >> k >> far;
        auto ans = copied.query(q, k, far);
        require(ans == copied.query(q, k, far));
        for (int id : ans) cout << id << ' ';
        cout << '\n';
    }
}

int main()
{
    int d;
    cin >> d;
    if (d == 1) run<1>();
    if (d == 2) run<2>();
    if (d == 3) run<3>();
    if (d == 5) run<5>();
    if (d == 10) run<10>();
}
