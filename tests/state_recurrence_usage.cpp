#include <bits/stdc++.h>
#include "../src/compact/recurrence.hpp"
#include "../src/compact/bostan_mori.hpp"
using namespace std;
int main() {
    for (int p : {2, 3, 5, 998244353}) {
        assert((berlekamp_massey({0, 1, 0, 0}, p) == vector<int>{0, 0}));
        assert((berlekamp_massey({0, 1, 0, 1}, p) == vector<int>{0, 1}));
        assert(recurrence_nth({0, 1}, {0, 0}, 1, p) == 1);
        assert(recurrence_nth({}, {}, 1, p) == 0);
        assert((berlekamp_massey({1, 1, 1, 1}, p) == vector<int>{1}));
    }
    // diag(1,2) over F2: distinct eigenvalues 1 and 0, scalar projection all ones.
    assert(1 % 2 != 2 % 2);
    int count; cin >> count;
    unsigned long long checks=0,bm_checks=0,bostan_checks=0;
    const vector<unsigned long long> remote={21,64,1000000000000000000ULL,ULLONG_MAX};
    for(int z=0;z<count;z++) {
        string id; int d,p,prime;cin>>id>>d>>p>>prime;
        vector<int> c(d),seq(21),later(4);
        for(auto &x:c)cin>>x;
        for(auto &x:seq)cin>>x;
        for(auto &x:later)cin>>x;
        auto verify=[&](const vector<int>& coeff,bool learned) {
            vector<int> init(seq.begin(),seq.begin()+coeff.size());
            assert(coeff.size()<=unsigned(d));
            for(int j=0;j<25;j++) {
                auto n=j<21?static_cast<unsigned long long>(j):remote[j-21];
                int want=j<21?seq[j]:later[j-21];
                assert(recurrence_nth(init,coeff,n,p)==want);checks++;
                if(learned)bm_checks++;
                if(p==998244353) {
                    using B=BostanMori<>;
                    B::Poly a(init.begin(),init.end()),b(coeff.begin(),coeff.end());
                    assert(B::recurrence(a,b,n).v==want);bostan_checks++;
                }
            }
        };
        verify(c,false);
        if(prime) {
            vector<int> prefix(seq.begin(),seq.begin()+2*d);
            auto learned=berlekamp_massey(prefix,p);
            verify(learned,true);
            if(id=="nilpotent_impulse")assert(learned==vector<int>({0,0,0}));
            if(id=="zero_output")assert(learned.empty());
            if(id=="unreachable")assert(learned==vector<int>({1}));
        }
    }
    assert(cin.good());
    cout<<"PASS cases="<<count<<" recurrence_nth="<<checks<<" BM-derived="<<bm_checks<<" BostanMori="<<bostan_checks<<'\n';
}
