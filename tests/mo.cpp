#include "../src/compact/tree_mo.hpp"
#include "../src/compact/rollback_mo.hpp"

void need(bool ok)
{
    if (!ok) abort();
}

int main()
{
    mt19937 rng(354355);
    for (int test = 0; test < 1500; test++)
    {
        int n = 1 + rng() % 40;
        HLD tree(n);
        for (int v = 2; v <= n; v++) tree.add(v, 1 + rng() % (v - 1));
        tree.build(1 + rng() % n);
        TreeMo mo(tree);
        vector<vector<int>> want;
        for (int i = 0; i < 100; i++)
        {
            int u = 1 + rng() % n, v = 1 + rng() % n;
            bool edge = rng() % 2;
            mo.add(u, v, edge);
            vector<int> expected(n + 1);
            while (u != v)
            {
                if (tree.dep[u] < tree.dep[v]) swap(u, v);
                expected[u] = 1;
                u = tree.fa[u];
            }
            if (!edge) expected[u] = 1;
            want.push_back(expected);
        }
        vector<int> actual(n + 1);
        for (int block : {0, 1, 7, 100})
        {
            mo.run([&](int u)
            {
                need(actual[u] == 0);
                actual[u]++;
            }, [&](int u)
            {
                need(actual[u] == 1);
                actual[u]--;
            }, [&](int id)
            {
                need(actual == want[id]);
            }, block);
            need(actual == vector<int>(n + 1));
        }
    }
    for (int test = 0; test < 1500; test++)
    {
        int n = rng() % 50;
        RollbackMo mo(n);
        vector<vector<int>> want;
        for (int i = 0; i < 100; i++)
        {
            int l = rng() % (n + 1), r = rng() % (n + 1);
            if (l > r) swap(l, r);
            mo.add(l, r);
            vector<int> expected(n);
            fill(expected.begin() + l, expected.begin() + r, 1);
            want.push_back(expected);
        }
        vector<int> actual(n), history;
        for (int block : {0, 1, 7, 100})
        {
            mo.run([&](int i)
            {
                need(actual[i] == 0);
                actual[i]++;
                history.push_back(i);
            }, [&]()
            {
                return history.size();
            }, [&](size_t saved)
            {
                while (history.size() > saved)
                {
                    actual[history.back()]--;
                    history.pop_back();
                }
            }, [&](int id)
            {
                need(actual == want[id]);
            }, block);
            need(history.empty());
            need(actual == vector<int>(n));
        }
    }
    cout << "PASS 1500 trees and 1500 interval sets, four block sizes\n";
}
