#include "../src/compact/cartesian_tree.hpp"

int main()
{
    int n = 10000000;
    for (int mode = 0; mode < 3; mode++)
    {
        vector<int> a(n);
        for (int i = 0; i < n; i++)
            a[i] = mode == 0 ? i : mode == 1 ? n - i : 0;
        auto begin = chrono::steady_clock::now();
        auto t = cartesian_tree(a);
        if (t.root != (mode == 1 ? n - 1 : 0)) abort();
        for (int i = 0; i < n; i++)
        {
            int left = mode == 1 && i ? i - 1 : -1;
            int right = mode != 1 && i + 1 < n ? i + 1 : -1;
            if (t.left[i] != left || t.right[i] != right) abort();
        }
        cout << mode << ' '
             << chrono::duration<double>(chrono::steady_clock::now() - begin).count() << '\n';
    }
}
