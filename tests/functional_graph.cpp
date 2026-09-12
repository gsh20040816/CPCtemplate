#include <bits/stdc++.h>
#include <cassert>
namespace compact {
#include "../src/compact/functional_graph.hpp"
}
namespace classic {
#include "../src/classic/functional_graph.hpp"
}
using namespace std;
using U=unsigned long long;
void check(const vector<int>&to)
{
    compact::FunctionalGraph a(to);
    classic::Functional_Graph b(to);
    int n=to.size();
    vector<int> count(n),peel(n,-1);
    for(int i=0;i<int(a.order.size());i++) peel[a.order[i]]=i;
    for(int id=0;id<int(a.cycles.size());id++)
        for(int i=0;i<int(a.cycles[id].size());i++)
        {
            int u=a.cycles[id][i];
            count[u]++;
            assert(a.component[u]==id && a.position[u]==i && a.entry[u]==u && a.depth[u]==0);
            assert(to[u]==a.cycles[id][(i+1)%a.cycles[id].size()]);
        }
    for(int u:a.order)
    {
        count[u]++;
        assert(a.depth[u]>0 && a.position[u]==-1);
        assert(peel[to[u]]==-1 || peel[u]<peel[to[u]]);
    }
    for(int c:count) assert(c==1);
    for(int start=0;start<n;start++)
    {
        vector<int> seen(n,-1),path;
        int u=start;
        while(seen[u]==-1)
        {
            seen[u]=path.size();
            path.push_back(u);
            u=to[u];
        }
        int tail=seen[u],length=path.size()-tail;
        assert(a.depth[start]==tail && b.depth[start]==tail);
        assert(a.entry[start]==u && b.entry[start]==u);
        assert(int(a.cycles[a.component[start]].size())==length);
        assert(int(b.cycles[b.component[start]].size())==length);
        for(int v=0;v<n;v++)
            assert(a.steps(start,v)==seen[v] && b.Steps(start,v)==seen[v]);
        vector<U> steps={0,1,U(n),U(n+1),1ULL<<63,~U(0),~U(0)-1};
        for(int k=0;k<=2*n;k++) steps.push_back(k);
        for(U k:steps)
        {
            int want=k<U(path.size())?path[k]:path[tail+(k-tail)%length];
            assert(a.advance(start,k)==want && b.Advance(start,k)==want);
        }
    }
    // Rebuild from a table owned by the same object, then clear and rebuild again.
    a.build(a.up[0]);
    b.Build(b.up[0]);
    for(int i=0;i<n;i++) assert(a.advance(i,1)==to[i] && b.Advance(i,1)==to[i]);
    a.build({});
    b.Build({});
    assert(a.n==0 && a.cycles.empty() && a.order.empty());
    assert(b.n==0 && b.cycles.empty() && b.order.empty());
    a.build(to);
    b.Build(to);
    for(int i=0;i<n;i++) assert(a.steps(i,to[i])==(to[i]==i?0:1));
}
void large()
{
    int n=500000,entry=123456,length=n-entry;
    vector<int> to(n);
    for(int i=0;i<n-1;i++) to[i]=i+1;
    to[n-1]=entry;
    compact::FunctionalGraph a(to);
    classic::Functional_Graph b(to);
    for(int i=0;i<n;i++)
    {
        assert(a.depth[i]==max(0,entry-i));
        U k=~U(0)-i;
        U tail=max(0,entry-i);
        int begin=max(entry,i);
        int want=entry+(U(begin-entry)+(k-tail)%length)%length;
        assert(a.advance(i,k)==want && b.Advance(i,k)==want);
        int target=(i*31LL)%n;
        int distance=target>=i?target-i:target>=entry?n-i+target-entry:-1;
        assert(a.steps(i,target)==distance && b.Steps(i,target)==distance);
    }
    assert(a.up.size()<=20 && b.up.size()<=20);
    iota(to.begin(),to.end(),0);
    a.build(to);
    b.Build(to);
    assert(a.cycles.size()==size_t(n) && b.cycles.size()==size_t(n));
    for(int i=0;i<n;i++) assert(a.advance(i,~U(0))==i && b.Advance(i,~U(0))==i);
}
int main()
{
    check({});
    for(int n=1;n<=5;n++)
    {
        int total=1;
        for(int i=0;i<n;i++) total*=n;
        for(int mask=0;mask<total;mask++)
        {
            int x=mask;
            vector<int> to(n);
            for(int &v:to) {v=x%n; x/=n;}
            check(to);
        }
    }
    mt19937 rng(17501160);
    for(int t=0;t<200;t++)
    {
        int n=1+rng()%50;
        vector<int> to(n);
        for(int &v:to) v=rng()%n;
        check(to);
    }
    large();
    cout << "Functional graph dual exhaustive successor maps, first-visit path oracles, uint64 jumps, rebuild and 500000 tail/cycle/self-loop cases PASS\n";
}
