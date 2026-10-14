#pragma once
#include <bits/stdc++.h>
#include <cassert>
#include <ext/rope>
#include <ext/pb_ds/priority_queue.hpp>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>
using namespace std;

// BEGIN rp
template <class T> using rp = __gnu_cxx::rope<T>;
// END rp

// BEGIN pheap
template <class T, class C = less<T>>
using pheap = __gnu_pbds::priority_queue<T, C, __gnu_pbds::pairing_heap_tag>;
// END pheap

// BEGIN ost
template <class T, class C = less<T>>
using ost = __gnu_pbds::tree<T,
                             __gnu_pbds::null_type,
                             C,
                             __gnu_pbds::rb_tree_tag,
                             __gnu_pbds::tree_order_statistics_node_update>;
// END ost

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
template <class K, class V> using cc_map = __gnu_pbds::cc_hash_table<K, V, hash64>;
// END gp_map
