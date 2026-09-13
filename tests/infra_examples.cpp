#include <bits/stdc++.h>
#include <cassert>
#include "../src/compact/pbds_heap.hpp"
using namespace std;
struct Trace
{
    static inline int copies=0,moves=0;
    Trace() = default;
    Trace(const Trace&) { copies++; }
    Trace(Trace&&) noexcept { moves++; }
};
int main()
{
    Trace a;
    auto &&r=std::move(a);
    assert(&r==&a && Trace::copies==0 && Trace::moves==0);
    Trace b(std::move(a));
    const Trace c;
    Trace d(std::move(c));
    assert(Trace::copies==1 && Trace::moves==1);
    vector<int> x{1,2,3};
    vector<int> y=std::move(x);
    assert((y==vector<int>{1,2,3}));
    x.clear();x.push_back(7);assert(x[0]==7);
    const vector<int> z{4,5};
    vector<int> w=std::move(z);
    w[0]=9;assert(z[0]==4);
    vector<int> v{3,2,3,7,1};
    sort(v.begin(),v.end());v.erase(unique(v.begin(),v.end()),v.end());
    assert((v==vector<int>{1,2,3,7}));
    assert(*lower_bound(v.begin(),v.end(),7)==7);
    priority_queue<int,vector<int>,greater<int>> q;
    q.push(7);q.push(2);assert(q.top()==2);q.pop();assert(q.top()==7);
    multiset<int> s{3,3,4};s.erase(s.find(3));assert(s.count(3)==1);
    optional<int> zero=0;assert(zero && *zero==0);
    vector<int> big(3,1000000000);assert(accumulate(big.begin(),big.end(),0LL)==3000000000LL);
    static_assert(countr_zero(0u)==numeric_limits<unsigned>::digits);
    pheap<int> first,second;
    auto h=first.push(7);first.modify(h,2);second.join(first);
    assert(first.empty() && second.top()==2);second.erase(h);assert(second.empty());
    cout << "Infra C++ examples: move/copy dispatch, valid moved-from reuse, STL ranges and PBDS ownership PASS\n";
}
