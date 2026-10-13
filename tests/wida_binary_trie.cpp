#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_binary_trie/main.cpp"

int main(int argc, char **argv)
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string mode = argc > 1 ? argv[1] : "";
    if (mode == "raw")
    {
        add(0, 3);
        cout << trie[1][0] << ' ' << f[1] << ' ' << tot << '\n';
        return 0;
    }
    newNode();
    if (mode == "sentinel")
        f[0] = inf;
    int n;
    cin >> n;
    for (int k = 0; k < n; k++)
    {
        int x, i;
        cin >> x >> i;
        add(x, i);
    }
    int q;
    cin >> q;
    for (int k = 0; k < q; k++)
    {
        int a, b;
        cin >> a >> b;
        cout << query(a, b) << '\n';
    }
    cout << f[0] << '\n';
}
