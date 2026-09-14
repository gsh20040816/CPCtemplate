#include "../src/classic/enclosing_circle.hpp"
#include "../src/compact/enclosing_circle.hpp"
#include <boost/multiprecision/cpp_dec_float.hpp>
using B = boost::multiprecision::cpp_dec_float_100;
using G = RealPlane;
using P = G::Point;
using R = G::R;
struct Ref { B x,y,r2; };

B distance2(B x, B y, P p)
{
    B dx=x-B(p.x), dy=y-B(p.y);
    return dx*dx+dy*dy;
}

Ref oracle(vector<P> p)
{
    vector<Ref> candidates;
    for (auto a:p)
        candidates.push_back({B(a.x),B(a.y),0});
    for (int i=0;i<(int)p.size();i++)
        for (int j=0;j<i;j++)
        {
            B x=(B(p[i].x)+p[j].x)/2, y=(B(p[i].y)+p[j].y)/2;
            candidates.push_back({x,y,distance2(x,y,p[i])});
            for (int k=0;k<j;k++)
            {
                // Solve the unscaled perpendicular-bisector equations in 100 digits.
                B ux=B(p[j].x)-p[i].x, uy=B(p[j].y)-p[i].y;
                B vx=B(p[k].x)-p[i].x, vy=B(p[k].y)-p[i].y;
                B d=2*(ux*vy-uy*vx);
                if (d==0) continue;
                B u=ux*ux+uy*uy, v=vx*vx+vy*vy;
                B cx=B(p[i].x)+(u*vy-v*uy)/d;
                B cy=B(p[i].y)+(ux*v-vx*u)/d;
                candidates.push_back({cx,cy,distance2(cx,cy,p[i])});
            }
        }
    Ref best{0,0,B("1e300")};
    for (auto c:candidates)
    {
        bool good=true;
        for (auto a:p)
            if (distance2(c.x,c.y,a)>c.r2+B("1e-70")*max(B(1),c.r2)) good=false;
        if (good && c.r2<best.r2) best=c;
    }
    return best;
}

void check(vector<P> p, Ref expected)
{
    vector<Real_Geometry::Point> q;
    for (auto a:p) q.push_back({a.x,a.y});
    for (int seed=0;seed<12;seed++)
    {
        mt19937_64 rng(seed), old_rng(seed);
        auto a=EnclosingCircle::solve(p,rng);
        auto b=Enclosing_Circle::Solve(q,old_rng);
        assert(a && b);
        assert(a->o.x==b->o.x && a->o.y==b->o.y && a->r==b->r);
        B radius=sqrt(expected.r2);
        B tol=B("2e-10")*max(B(1),radius);
        assert(abs(B(a->r)-radius)<tol);
        assert(abs(B(a->o.x)-expected.x)<tol);
        assert(abs(B(a->o.y)-expected.y)<tol);
        for (auto v:p)
            assert(sqrt(distance2(B(a->o.x),B(a->o.y),v))<=B(a->r)+tol);
    }
}

int main()
{
    mt19937_64 rng(1742);
    assert(!EnclosingCircle::solve({},rng));
    assert(!Enclosing_Circle::Solve({},rng));
    for (int t=0;t<700;t++)
    {
        vector<P> p;
        for (int i=0,n=1+rng()%10;i<n;i++)
            p.push_back({R(int(rng()%2001)-1000)/100,R(int(rng()%2001)-1000)/100});
        check(p,oracle(p));
    }
    for (vector<P> p: {vector<P>{{0,0},{1,0},{2,0},{2,0}},
                        vector<P>{{0,0},{2,0},{1,1e-12L}},
                        vector<P>{{0,0},{2,0},{1,2}},
                        vector<P>{{10000,10000},{9999.99L,10000},{10000,9999.99L}}})
        check(p,oracle(p));
    vector<P> p;
    for (int i=0;i<100000;i++)
        p.push_back({R(i%20001)-10000,0});
    check(p,{0,0,B(100000000)});
    p.assign(100000,{3,4});
    check(p,{3,4,0});
    cout << "Enclosing circle dual 100-digit support enumeration, multiple shuffle seeds, collinear/duplicate points and 100000 points PASS\n";
}
