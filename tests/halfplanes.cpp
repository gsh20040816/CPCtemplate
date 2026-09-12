#include "../src/classic/halfplanes.hpp"
#include "../src/compact/halfplanes.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <set>
#include <numeric>
#include <random>
#include <iostream>
using boost::multiprecision::cpp_int;
using H=IntegerHalfplanes;
using Key=tuple<long long,long long,long long>;

Key normalize(long long x,long long y,long long d)
{
    long long g=gcd(gcd(x,y),d);
    return {x/g,y/g,d/g};
}

void check(vector<H::Line> lines)
{
    set<Key> expected;
    for(int i=0;i<(int)lines.size();i++)
        for(int j=0;j<i;j++)
        {
            auto u=lines[i],v=lines[j];
            cpp_int d=cpp_int(u.a)*v.b-cpp_int(u.b)*v.a;
            if(d==0)
                continue;
            cpp_int x=cpp_int(u.c)*v.b-cpp_int(u.b)*v.c;
            cpp_int y=cpp_int(u.a)*v.c-cpp_int(u.c)*v.a;
            if(d<0)
            {
                d=-d;
                x=-x;
                y=-y;
            }
            bool ok=true;
            for(auto line:lines)
                if(line.a*x+line.b*y>line.c*d)
                    ok=false;
            if(ok)
                expected.insert(normalize(x.convert_to<long long>(),y.convert_to<long long>(),d.convert_to<long long>()));
        }
    if(expected.size()<3)
        expected.clear();
    auto result=H::bounded_polygon(lines);
    vector<Integer_Halfplanes::Line> other;
    for(auto u:lines)
        other.push_back({u.a,u.b,u.c});
    auto classic=Integer_Halfplanes::Bounded_Polygon(other);
    set<Key> actual,second;
    for(auto p:result)
        actual.insert(normalize(p.x,p.y,p.d));
    for(auto p:classic)
        second.insert(normalize(p.x,p.y,p.d));
    assert(actual==expected && second==expected);
    assert(actual.size()==result.size() && second.size()==classic.size());
    // Cyclic order must describe a convex polygon, checked in arbitrary precision.
    for(int i=0;i<(int)result.size();i++)
    {
        auto p=result[i],q=result[(i+1)%result.size()],r=result[(i+2)%result.size()];
        cpp_int ax=cpp_int(q.x)*p.d-cpp_int(p.x)*q.d;
        cpp_int ay=cpp_int(q.y)*p.d-cpp_int(p.y)*q.d;
        cpp_int bx=cpp_int(r.x)*q.d-cpp_int(q.x)*r.d;
        cpp_int by=cpp_int(r.y)*q.d-cpp_int(q.y)*r.d;
        assert(ax*by-ay*bx>0);
    }
}

int main()
{
    vector<H::Line> box={{1,0,10},{-1,0,10},{0,1,10},{0,-1,10}};
    check(box);
    for(auto extra:vector<vector<H::Line>>{{{1,0,0},{-1,0,0}},{{1,0,-1},{-1,0,-1}},{{1,0,0},{-1,0,0},{0,1,0},{0,-1,0}},{{0,0,-1}},{{0,0,0}},{{2,0,20},{3,0,15}},{{1,1,0},{-1,-1,0}}})
    {
        auto h=box;
        h.insert(h.end(),extra.begin(),extra.end());
        check(h);
    }
    mt19937 rng(4196);
    for(int t=0;t<5000;t++)
    {
        auto h=box;
        for(int i=0;i<8;i++)
            h.push_back({int(rng()%11)-5,int(rng()%11)-5,int(rng()%51)-25});
        shuffle(h.begin(),h.end(),rng);
        check(h);
    }
    auto big=vector<H::Line>{{1,0,1000000000},{-1,0,1000000000},{0,1,1000000000},{0,-1,1000000000},
        {1000000000,999999999,1000000000},{999999999,999999998,999999999}};
    check(big);
    vector<H::Line> many={{1,0,1},{-1,0,1},{0,1,1},{0,-1,1}};
    for(int i=0;i<100000;i++)
    {
        long long a=int(rng()%200001)-100000;
        long long b=int(rng()%200001)-100000;
        many.push_back({a,b,abs(a)+abs(b)+1});
    }
    auto p=H::bounded_polygon(many);
    set<Key> square={{-1,-1,1},{-1,1,1},{1,-1,1},{1,1,1}};
    set<Key> got;
    for(auto v:p)
        got.insert(normalize(v.x,v.y,v.d));
    assert(got==square && p.size()==4);
    vector<Integer_Halfplanes::Line> classic;
    for(auto h:many)
        classic.push_back({h.a,h.b,h.c});
    auto q=Integer_Halfplanes::Bounded_Polygon(classic);
    got.clear();
    for(auto v:q)
        got.insert(normalize(v.x,v.y,v.d));
    assert(got==square && q.size()==4);
    cout << "Integer halfplanes dual cpp_int pair-intersection oracle, parallel/degenerate cases and near-parallel billion coefficients and 100000 redundant constraints PASS\n";
}
