#include <chrono>
#include <iostream>
#include <random>
#include "../src/compact/dynamic_peach_tree.hpp"
int main()
{
    std::mt19937 rng(1942);
    for (int shape = 0; shape < 3; shape++)
    {
        int n = 200000;
        std::vector<int> p(n, -1);
        std::vector<long long> b(n);
        for (int i = 1; i < n; i++)
            p[i] = shape == 0 ? i - 1 : shape == 1 ? 0 : rng() % i;
        auto start = std::chrono::steady_clock::now();
        DynamicPeachTree tree(p, b);
        assert(tree.add(1, 0, 200000000000LL));
        long long supply = 200000000000LL;
        for (int j = 0; j < 200000; j++)
        {
            int type = 1 + rng() % 2;
            int x = rng() % n;
            long long value = 1 + rng() % 1000000;
            supply += type == 1 ? value : -value;
            assert(tree.add(type, x, value));
            assert(tree.ans[0] == -supply);
        }
        assert(!tree.add(2, 0, supply + 1));
        std::cout << shape << ' ' << std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count() << '\n';
    }
}
