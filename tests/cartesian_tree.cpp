#include "../src/compact/cartesian_tree.hpp"

void check(const vector<long long> &a)
{
    auto got = cartesian_tree(a);
    vector<int> left(a.size(), -1);
    vector<int> right(a.size(), -1);
    auto build = [&](auto &&self, int l, int r) -> int
    {
        if (l == r) return -1;
        int m = min_element(a.begin() + l, a.begin() + r) - a.begin();
        left[m] = self(self, l, m);
        right[m] = self(self, m + 1, r);
        return m;
    };
    int root = build(build, 0, a.size());
    if (got.root != root || got.left != left || got.right != right) abort();
}

int main()
{
    int cases = 0;
    for (int n = 0; n <= 9; n++)
    {
        int count = 1;
        for (int i = 0; i < n; i++) count *= 3;
        for (int mask = 0; mask < count; mask++)
        {
            vector<long long> a(n);
            int x = mask;
            for (auto &v : a)
            {
                v = x % 3 - 1;
                x /= 3;
            }
            check(a);
            cases++;
        }
    }
    mt19937_64 rng(5854);
    for (int test = 0; test < 1000; test++)
    {
        vector<long long> a(rng() % 200);
        for (auto &v : a) v = (long long)rng();
        check(a);
        cases++;
    }
    check({LLONG_MAX, LLONG_MIN, LLONG_MIN, LLONG_MAX});
    cout << cases + 1 << " independent recursive argmin cases PASS\n";
}
