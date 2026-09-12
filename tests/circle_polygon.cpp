#include "../src/classic/circle_polygon.hpp"
#include "../src/compact/circle_polygon.hpp"
#include <boost/multiprecision/cpp_dec_float.hpp>
using B = boost::multiprecision::cpp_dec_float_100;
using G = RealGeometry;
using R = G::R;
using P = G::Point;
using C = G::Circle;

// Independent vertical-slice integration, including concave polygons.
R oracle(vector<P> p, C c)
{
    for (auto &v:p) v=v-c.o;
    vector<R> xs{-c.r,c.r};
    for (auto v:p) if (-c.r<v.x && v.x<c.r) xs.push_back(v.x);
    sort(xs.begin(),xs.end());
    auto f=[&](R x)
    {
        vector<R> ys;
        for (int i=0;i<(int)p.size();i++)
        {
            P a=p[i],b=p[(i+1)%p.size()];
            if ((a.x<=x && b.x>x)||(b.x<=x && a.x>x))
                ys.push_back(a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x));
        }
        sort(ys.begin(),ys.end());
        R y=sqrtl(max(R(0),c.r*c.r-x*x)), result=0;
        for (int i=1;i<(int)ys.size();i+=2)
            result+=max(R(0),min(y,ys[i])-max(-y,ys[i-1]));
        return result;
    };
    function<R(R,R,R,R,R,R,int)> integrate=[&](R l,R r,R a,R b,R m,R tolerance,int depth)->R
    {
        R mid=(l+r)/2;
        R x=f((l+mid)/2),y=f((mid+r)/2);
        R whole=(r-l)*(a+4*m+b)/6;
        R halves=(r-l)*(a+4*x+2*m+4*y+b)/12;
        if (!depth || fabsl(halves-whole)<15*tolerance)
            return halves+(halves-whole)/15;
        return integrate(l,mid,a,m,x,tolerance/2,depth-1)+integrate(mid,r,m,b,y,tolerance/2,depth-1);
    };
    R answer=0;
    for (int i=1;i<(int)xs.size();i++)
    {
        R l=xs[i-1],r=xs[i];
        if (l==r) continue;
        // One-sided samples avoid vertex/vertical-edge endpoint discontinuities.
        answer+=integrate(l,r,f(nextafterl(l,r)),f(nextafterl(r,l)),f((l+r)/2),1e-12L,28);
    }
    return answer;
}

void check(vector<P> p,C c,R want,R tolerance=2e-8L)
{
    vector<Real_Geometry::Point> q;
    for (auto a:p) q.push_back({a.x,a.y});
    auto a=CirclePolygon::area(p,c);
    auto b=Circle_Polygon::Area(q,{{c.o.x,c.o.y},c.r});
    assert(a==b && isfinite(a));
    if (fabsl(a-want)>tolerance)
    {
        cerr<<setprecision(20)<<a<<" vs "<<want<<"\n";
        abort();
    }
    reverse(p.begin(),p.end());
    assert(fabsl(CirclePolygon::area(p,c)-a)<tolerance);
}

int main()
{
    R pi=acosl(-1.L);
    check({},{{0,0},1},0);
    check({{0,0},{1,0}},{{0,0},1},0);
    vector<P> square{{-2,-2},{2,-2},{2,2},{-2,2}};
    check(square,{{0,0},1},pi);
    check(square,{{0,0},0},0);
    check(square,{{0,0},10},16);
    check(square,{{10,10},1},0);
    check({{0,-2},{2,-2},{2,2},{0,2}},{{0,0},1},pi/2);
    check({{0,0},{2,0},{2,2},{0,2}},{{0,0},1},pi/4);
    check({{-2,1},{2,1},{2,2},{-2,2}},{{0,0},1},0);
    for (R x:{-0.9L,-0.5L,0.L,0.5L,0.9L,1-1e-8L})
    {
        B bx=x;
        R cap=(acos(bx)-bx*sqrt(1-bx*bx)).convert_to<R>();
        check({{x,-2},{2,-2},{2,2},{x,2}},{{0,0},1},cap,1e-12L);
    }
    check({{-1e30L,-1e30L},{1e30L,-1e30L},{1e30L,1e30L},{-1e30L,1e30L}},{{0,0},1},pi);
    check({{-1e30L,0},{1e30L,0},{1e30L,1e30L},{-1e30L,1e30L}},{{0,0},1},pi/2);
    mt19937 rng(3675);
    for (int t=0;t<150;t++)
    {
        vector<P> p;
        int n=3+rng()%8;
        for (int i=0;i<n;i++)
        {
            R a=2*pi*i/n,r=0.5L+R(rng()%300)/100;
            p.push_back({r*cosl(a),r*sinl(a)});
        }
        C c{{R(int(rng()%101)-50)/100,R(int(rng()%101)-50)/100},1.3L};
        R want=oracle(p,c);
        check(p,c,want);
        p.insert(p.begin(),p[0]);
        check(p,c,want);
        for (auto &v:p) v=v+P{100,200};
        c.o=c.o+P{100,200};
        check(p,c,want);
    }
    vector<P> large;
    for (int i=0;i<100000;i++)
    {
        R angle=2*pi*i/100000;
        large.push_back({cosl(angle),sinl(angle)});
    }
    check(large,{{0,0},2},50000*sinl(2*pi/100000),1e-12L);
    for (R scale:{1e-50L,1e50L})
    {
        vector<P> p{{0,-2*scale},{2*scale,-2*scale},{2*scale,2*scale},{0,2*scale}};
        check(p,{{0,0},scale},pi/2*scale*scale,1e-12L*scale*scale);
    }
    cout<<"Circle polygon dual analytic disk/cap cases, independent vertical-slice integration, concavity, orientation and duplicate vertices PASS\n";
}
