#include "../../src/compact/leftist_heap.hpp"
#include "../../src/compact/data_structure.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    LeftistHeap heap;
    dsu sets(n);
    vector<int> root(n);
    vector<bool> removed(n);
    for (int i = 0; i < n; i++)
    {
        long long key;
        cin >> key;
        root[i] = heap.singleton(key);
    }
    while (m--)
    {
        int op, x;
        cin >> op >> x;
        x--;
        if (op == 1)
        {
            int y;
            cin >> y;
            y--;
            if (removed[x] || removed[y]) continue;
            int a = sets.find(x), b = sets.find(y);
            if (a == b) continue;
            root[a] = heap.meld(root[a], root[b]);
            sets.merge(a, b);
        }
        else if (removed[x])
            cout << -1 << '\n';
        else
        {
            int a = sets.find(x), id = root[a];
            cout << heap.t[id].key << '\n';
            removed[id - 1] = true;
            root[a] = heap.pop(id);
        }
    }
}
