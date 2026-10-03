#include <iostream>
#include "../../src/compact/persistent_xor_trie.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    PersistentXorTrie trie(24, n + m + 1);
    uint64_t sum = 0, x;
    trie.append(0);
    for (int i = 0; i < n; i++)
    {
        cin >> x;
        sum ^= x;
        trie.append(sum);
    }
    while (m--)
    {
        char op;
        cin >> op;
        if (op == 'A')
        {
            cin >> x;
            sum ^= x;
            trie.append(sum);
        }
        else
        {
            int l, r;
            cin >> l >> r >> x;
            cout << *trie.max_xor(l - 1, r, sum ^ x) << '\n';
        }
    }
}
