// https://judge.yosupo.jp/problem/persistent_queue
#include <bits/stdc++.h>
#include <ext/rope>
#include <cassert>
using namespace std;

// BEGIN rp
template <class T> using rp = __gnu_cxx::rope<T>;
// END rp


int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q;
    cin >> q;
    vector<rp<int>> s(q + 1);
    for (int i = 1; i <= q; i++)
    {
        int op, t, x;
        cin >> op >> t;
        s[i] = s[t + 1];
        if (op == 0)
        {
            cin >> x;
            s[i].push_back(x);
        }
        else
        {
            cout << s[i][0] << '\n';
            s[i].erase(0, 1);
        }
    }
}
