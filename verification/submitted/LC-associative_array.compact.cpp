// https://judge.yosupo.jp/problem/associative_array
#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
using namespace std;

// BEGIN gp_map
struct hash64
{
    static uint64_t mix(uint64_t x)
    {
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }

    size_t operator()(uint64_t x) const
    {
        static const uint64_t seed =
            chrono::steady_clock::now().time_since_epoch().count();
        return mix(x + seed);
    }
};

template <class K, class V> using gp_map = __gnu_pbds::gp_hash_table<K, V, hash64>;
// END gp_map


int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q;
    cin >> q;
    gp_map<uint64_t, uint64_t> a;
    while (q--)
    {
        int op;
        uint64_t k, v;
        cin >> op >> k;
        if (op == 0)
        {
            cin >> v;
            a[k] = v;
        }
        else
        {
            auto it = a.find(k);
            cout << (it == a.end() ? 0 : it->second) << '\n';
        }
    }
}
