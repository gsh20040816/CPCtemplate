#include "../src/compact/affine_sequence.hpp"
#include <climits>
#include <iostream>
#include <string>

using I = __int128_t;
using V = std::vector<int>;
static unsigned long long checks = 0;
static void require(bool ok, const char* what) {
    ++checks;
    if (!ok) { std::cerr << "FAIL " << what << '\n'; std::abort(); }
}
template<int M> int norm(I x) { x %= M; if (x < 0) x += M; return int(x); }
template<int M> int sum(const V& v, int l, int r) {
    I s = 0; for (int i = l; i < r; ++i) s += v[i]; return norm<M>(s);
}
template<int M> void apply(V& v, int l, int r, long long b, long long c) {
    for (int i = l; i < r; ++i) v[i] = norm<M>(I(b) * v[i] + c);
}
template<int M> std::pair<int,int> inspect(AffineSequenceTreap<M>& t, int p, V& out, std::vector<bool>& seen) {
    if (!p) return {0,0};
    require(p > 0 && size_t(p) < t.a.size(), "node index");
    require(!seen[p], "cycle or shared child"); seen[p] = true;
    t.push(p);
    const auto node = t.a[p];
    require(!node.rev && node.mul.v == norm<M>(1) && !node.add.v, "pushed lazy identity");
    for (int child : {node.l,node.r}) {
        require(child >= 0 && size_t(child) < t.a.size(), "child index");
        if (child) require(node.pri >= t.a[child].pri, "priority heap");
    }
    auto l = inspect(t,node.l,out,seen);
    out.push_back(node.val.v);
    auto r = inspect(t,node.r,out,seen);
    int n = l.first+r.first+1, s=norm<M>(I(l.second)+node.val.v+r.second);
    require(node.siz == n, "recomputed size");
    require(node.sum.v == s, "recomputed sum");
    require(node.val.v >= 0 && node.val.v < M, "canonical value");
    return {n,s};
}
template<int M> void verify(const AffineSequenceTreap<M>& original, const V& expected, bool ranges=false) {
    require(original.size() == int(expected.size()), "public size");
    auto t = original; // Preserve pending tags in the test subject.
    V got; std::vector<bool> seen(t.a.size());
    auto aggregate = inspect(t,t.root,got,seen);
    require(got == expected, "independent in-order values");
    require(aggregate.second == sum<M>(expected,0,expected.size()), "root aggregate");
    require(t.a[0].siz == 0 && t.a[0].sum.v == 0 && !t.a[0].l && !t.a[0].r, "null sentinel");
    auto values = t.values();
    require(values.size() == expected.size(), "values size");
    for (size_t i=0;i<values.size();++i) require(values[i].v == expected[i], "values API");
    if (ranges) for (int l=0;l<int(expected.size());++l) for(int r=l+1;r<=int(expected.size());++r)
        require(t.query(l+1,r).v == sum<M>(expected,l,r), "all ranges");
}
template<int M> void exhaustive() {
    for (int n=0;n<=4;++n) {
        int count=1; for(int i=0;i<n;++i) count*=3;
        for(int mask=0;mask<count;++mask) {
            AffineSequenceTreap<M> base(mask+17); V v; int z=mask;
            for(int i=0;i<n;++i) { long long x=z%3-1; z/=3; base.insert(i,x); v.push_back(norm<M>(x)); }
            verify(base,v,true);
            for(int k=0;k<=n;++k) for(long long x : {-1LL,0LL,1LL,LLONG_MIN,LLONG_MAX}) {
                auto t=base; auto w=v; t.insert(k,x); w.insert(w.begin()+k,norm<M>(x)); verify(t,w,true);
            }
            for(int l=0;l<n;++l) for(int r=l+1;r<=n;++r) {
                auto t=base; auto w=v; t.erase(l+1,r); w.erase(w.begin()+l,w.begin()+r); verify(t,w,true);
                t=base; w=v; t.reverse(l+1,r); std::reverse(w.begin()+l,w.begin()+r); verify(t,w,true);
                for(long long b : {-1LL,0LL,1LL,2LL}) for(long long c : {-1LL,0LL,1LL,2LL}) {
                    t=base; w=v; t.affine(l+1,r,b,c); apply<M>(w,l,r,b,c);
                    // Compose without forcing pushes, then reverse a crossing range.
                    t.affine(1,n,3,-2); apply<M>(w,0,n,3,-2);
                    verify(t,w,true); // Check noncommuting composition before any zero overwrite.
                    t.reverse(1,n); std::reverse(w.begin(),w.end());
                    t.affine(l+1,r,0,5); apply<M>(w,l,r,0,5);
                    t.affine(1,n,-2,7); apply<M>(w,0,n,-2,7);
                    verify(t,w,true);
                }
            }
            verify(base,v,true); // Copies must never mutate the original.
        }
    }
}
template<int M> void randomized() {
    const long long special[] = {LLONG_MIN,LLONG_MAX,-1,0,1,-2147483648LL,2147483647LL};
    for(unsigned long long seed : {0ULL,1ULL,42ULL,712367821ULL,~0ULL}) {
        std::mt19937_64 rng(seed^0x8ab192ULL);
        AffineSequenceTreap<M> t(seed); V v;
        for(int step=0;step<12000;++step) {
            auto scalar=[&]() -> long long { return rng()%3 ? special[rng()%7] : static_cast<long long>(rng() & LLONG_MAX); };
            int op=rng()%7, n=v.size();
            if(!n || (op==0 && n<250)) {
                int k=rng()%(n+1); auto x=scalar(); t.insert(k,x); v.insert(v.begin()+k,norm<M>(x));
            } else {
                int l=rng()%n, r=l+1+rng()%(n-l);
                if(op==1) { t.erase(l+1,r); v.erase(v.begin()+l,v.begin()+r); }
                else if(op==2) { t.reverse(l+1,r); std::reverse(v.begin()+l,v.begin()+r); }
                else if(op<=4) { auto b=scalar(),c=scalar(); t.affine(l+1,r,b,c); apply<M>(v,l,r,b,c); }
                else require(t.query(l+1,r).v==sum<M>(v,l,r), "random range query");
            }
            if(step%31==0) verify(t,v);
            if(step%499==0) {
                auto copied=t; auto w=v;
                copied.insert(0,LLONG_MIN); w.insert(w.begin(),norm<M>(LLONG_MIN)); verify(copied,w);
                verify(t,v);
            }
        }
        if(t.size()) t.erase(1,t.size());
        v.clear(); verify(t,v);
        // Non-recycled nodes survive erase-all; vector reallocations need no reserve.
        for(int i=0;i<8193;++i) { t.insert(i,special[i%7]); v.push_back(norm<M>(special[i%7])); }
        verify(t,v); t.affine(1,t.size(),LLONG_MIN,LLONG_MAX); apply<M>(v,0,v.size(),LLONG_MIN,LLONG_MAX); verify(t,v);
        t = AffineSequenceTreap<M>(seed); verify(t,{}); require(t.a.size()==1,"reset via assignment");
    }
}
static void scale() {
    constexpr int M=998244353, N=500000, Q=500000;
    AffineSequenceTreap<M> t(987654321);
    for(int i=0;i<N;++i) t.insert(i,i); // Explicitly exercise pool growth without reserve.
    require(t.query(1,N).v==norm<M>(I(N)*(N-1)/2),"scale initial closed form");
    t.reverse(1,N); t.affine(1,N,7,11);
    std::mt19937_64 rng(123456789);
    for(int i=0;i<Q;++i) {
        int l=rng()%N, r=l+1+rng()%(N-l);
        I len=r-l, expected=7*(len*(N-1)-I(l+r-1)*len/2)+11*len;
        require(t.query(l+1,r).v==norm<M>(expected),"scale query closed form");
        if(i%10000==0) { t.reverse(1,N); t.reverse(1,N); }
    }
    t.affine(1,N,0,LLONG_MAX); t.affine(1,N,LLONG_MIN,37);
    int x=norm<M>(I(LLONG_MIN)*norm<M>(LLONG_MAX)+37);
    require(t.query(1,N).v==norm<M>(I(x)*N),"scale zero multiplier composition");
    t.erase(1,N); require(t.size()==0,"scale erase all");
    t.insert(0,LLONG_MIN); verify(t,{norm<M>(LLONG_MIN)},true);
}
int main(int argc,char**argv) {
    if(argc==2 && std::string(argv[1])=="--max") scale();
    else {
        exhaustive<1>(); exhaustive<2>(); exhaustive<5>(); exhaustive<998244353>();
        randomized<1>(); randomized<2>(); randomized<4>(); randomized<7>();
        randomized<1000>(); randomized<998244353>(); randomized<1000000007>(); randomized<INT_MAX>();
    }
    std::cout << "PASS affine sequence independent oracle; checks=" << checks << '\n';
}
