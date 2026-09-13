#pragma once
#include <bits/stdc++.h>
#include <ext/pb_ds/priority_queue.hpp>
#include <cassert>
using namespace std;

// BEGIN pheap
template <class T, class C = less<T>>
using pheap = __gnu_pbds::priority_queue<T, C, __gnu_pbds::pairing_heap_tag>;
// END pheap
