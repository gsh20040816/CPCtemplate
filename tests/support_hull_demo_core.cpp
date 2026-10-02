#include "../src/compact/support_hull.hpp"
#include <algorithm>
#include <random>
#include <iostream>
using P=SupportHull::Point; using I=__int128_t;
bool lessp(P a,P b){return a.x!=b.x?a.x<b.x:a.y<b.y;}
bool eq(P a,P b){return a.x==b.x&&a.y==b.y;}
I dot(P p,long long a,long long b){return I(p.x)*a+I(p.y)*b;}
P brute(const vector<P>& p,long long a,long long b,int mode=0){
 I best=-(I(1)<<126); vector<P> t;
 for(P z:p){I v=dot(z,a,b);if(v>best){best=v;t.clear();}if(v==best)t.push_back(z);}
 sort(t.begin(),t.end(),lessp);return t[mode==0?0:mode==1?t.size()-1:t.size()/2];
}
vector<P> build(const vector<P>&p,int mode){
 if(p.empty())return {};
 P l=*min_element(p.begin(),p.end(),lessp),r=l;
 for(P z:p)if(z.x>r.x||(z.x==r.x&&z.y<r.y))r=z;
 return SupportHull::build(l,r,[&](long long a,long long b){assert(b<0);return brute(p,a,b,mode);});
}
P query(const vector<P>&h,long long a,long long b){
 assert(!h.empty()&&b<=0);int l=0,r=int(h.size())-1;
 while(l<r){int m=(l+r)/2;if(dot(h[m],a,b)<dot(h[m+1],a,b))l=m+1;else r=m;}
 return h[l];
}
vector<P> chain(vector<P> p){
 sort(p.begin(),p.end(),lessp); vector<P> lowest,h;
 for(P z:p) if(lowest.empty()||lowest.back().x!=z.x) lowest.push_back(z);
 for(P z:lowest){while(h.size()>1){P a=h[h.size()-2],b=h.back();
 I turn=(I(b.x)-a.x)*(I(z.y)-a.y)-(I(b.y)-a.y)*(I(z.x)-a.x);
 if(turn>0)break;h.pop_back();}h.push_back(z);}return h;
}
long long cases=0,queries=0;
void check(const vector<P>&p,const vector<pair<long long,long long>>&qs){
 auto want=chain(p); for(int mode=0;mode<3;mode++){auto h=build(p,mode);assert(h.size()==want.size());for(int i=0;i<(int)h.size();i++)assert(eq(h[i],want[i]));for(auto[a,b]:qs){if(p.empty()){assert(h.empty());continue;}P got=query(h,a,b),want=brute(p,a,b);assert(eq(got,want)&&dot(got,a,b)==dot(want,a,b));queries++;}cases++;}
}
int main(){
 vector<pair<long long,long long>> qs;for(int a=-3;a<=3;a++)for(int b=-3;b<=0;b++)qs.push_back({a,b});
 check({},qs);for(int mask=1;mask<512;mask++){vector<P>p;for(int i=0;i<9;i++)if(mask>>i&1)p.push_back({i/3-1,i%3-1});check(p,qs);}
 mt19937_64 rng(712367);for(int t=0;t<3000;t++){vector<P>p;for(int i=0,n=rng()%81;i<n;i++)p.push_back({(long long)(rng()%31)-15,(long long)(rng()%31)-15});check(p,qs);}
 const long long B=1000000000000000000LL;
 vector<pair<long long,long long>> extreme={{-B,-B},{B,-B},{0,-B},{B,0},{-B,0},{0,0}};
 check({{-B,B},{-B,-B},{0,-B},{B,B},{B,-B},{0,0},{B,-B}},extreme);
 check({{-B,B},{0,-B},{B,B}},extreme);
 vector<P>p;for(int x=-1000;x<1000;x++)p.push_back({x,1LL*x*x});auto h=build(p,0);assert(h.size()==2000);
 for(int i=0;i<200000;i++){long long a=(long long)(rng()%4001)-2000,b=-1;P got=query(h,a,b),want=brute(p,a,b);assert(eq(got,want)&&dot(got,a,b)==dot(want,a,b));queries++;}
 cout<<"PASS separate custom core tie-policy harness: "<<cases<<" build cases; "<<queries<<" brute-force checked queries; maximum n=2000 q=200000\n";
}
