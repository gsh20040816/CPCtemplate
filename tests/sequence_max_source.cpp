#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <vector>
#include "../src/compact/sequence_max_treap.hpp"
std::mt19937 rng(19491001);
#include "fixtures/wida_sequence_max/08C.cpp"

void erase_tree(Node *p)
{
    if (!p)
        return;
    erase_tree(p->l);
    erase_tree(p->r);
    delete p;
}

void check(const std::vector<int> &a, const std::vector<int> &limits)
{
    SequenceMaxTreap tree;
    int root = 0;
    Node *old = nullptr;
    std::vector<int> expected;
    for (int i = 0; i < int(a.size()); i++)
    {
        int suffix = 0;
        for (int j = int(expected.size()) - 1; j >= 0; j--)
        {
            if (a[expected[j] - 1] > a[i])
                break;
            suffix++;
        }
        assert(query(old, a[i]) == suffix);
        assert(tree.last_greater(root, a[i]) == i - suffix - 1);
        int pos = std::max(i - limits[i], i - suffix);
        auto *p = new Node;
        p->info = {a[i], i + 1};
        p->sum = p->info;
        insertAt(old, pos, p);
        tree.insert(root, pos, a[i]);
        expected.push_back(i + 1);
        int j = i;
        int remaining = limits[i];
        while (j > 0 && remaining > 0 && a[expected[j - 1] - 1] < a[i])
        {
            std::swap(expected[j], expected[j - 1]);
            j--;
            remaining--;
        }
        assert(tree.ids(root) == expected);
        int cut = rng() % (i + 2);
        auto [left, right] = splitAt(old, cut);
        old = merge(left, right);
        std::ostringstream output;
        auto *saved = std::cout.rdbuf(output.rdbuf());
        dfs(old);
        std::cout.rdbuf(saved);
        std::istringstream input(output.str());
        for (int id : expected)
        {
            int actual = 0;
            input >> actual;
            assert(actual == id);
        }
        int extra;
        assert(!(input >> extra));
    }
    erase_tree(old);
}

int main()
{
    long long cases = 0;
    for (int n = 1; n <= 6; n++)
    {
        std::vector<int> a(n);
        std::iota(a.begin(), a.end(), 1);
        do
        {
            for (int mode = 0; mode < 5; mode++)
            {
                std::vector<int> limits(n);
                for (int i = 0; i < n; i++)
                    limits[i] = mode == 0 ? 0 : mode == 1 ? n : rng() % (n + 1);
                check(a, limits);
                cases++;
            }
        } while (std::next_permutation(a.begin(), a.end()));
    }
    for (int trial = 0; trial < 500; trial++)
    {
        int n = 1 + rng() % 150;
        std::vector<int> a(n), limits(n);
        std::iota(a.begin(), a.end(), 1);
        std::shuffle(a.begin(), a.end(), rng);
        for (int &v : limits)
            v = rng() % (n + 1);
        check(a, limits);
        cases++;
    }
    std::cout << cases << " original-source / adjacent-swap cases PASS\n";
}
