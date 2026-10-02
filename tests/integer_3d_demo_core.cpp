// Direct public primitives on point differences, never arbitrary int128 vectors.
#include <bits/stdc++.h>
using namespace std;
#include "../src/compact/geometry_extra.hpp"
int main()
{
    auto print = [](__int128_t x) {
        __uint128_t u = x < 0 ? __uint128_t(0)-__uint128_t(x) : __uint128_t(x);
        string s;
        do { s += char('0'+u%10); u/=10; } while(u);
        if(x<0) cout << '-';
        reverse(s.begin(),s.end()); cout << s;
    };
    int q; cin >> q;
    while(q--) {
        IntegerGeometry3D::Point a,b,c,d;
        for(auto p : {&a,&b,&c,&d}) cin >> p->x >> p->y >> p->z;
        auto u=IntegerGeometry3D::diff(b,a), v=IntegerGeometry3D::diff(d,c);
        auto w=IntegerGeometry3D::cross(u,v);
        for(auto x : {u.x,u.y,u.z,v.x,v.y,v.z,w.x,w.y,w.z}) { print(x); cout << ' '; }
        print(IntegerGeometry3D::dot(u,v)); cout << '\n';
    }
}
