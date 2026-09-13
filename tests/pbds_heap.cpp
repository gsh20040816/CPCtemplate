#include "../src/compact/pbds_heap.hpp"
int main()
{
    using P = pair<long long,int>;
    using H = pheap<P>;
    array<H,4> q;
    array<set<P>,4> ref;
    vector<H::point_iterator> handle;
    vector<int> owner;
    vector<long long> value;
    mt19937 rng(65310);
    auto forget = [&](int id)
    {
        ref[owner[id]].erase({value[id],id});
        owner[id] = -1;
    };
    vector<long long> edges{LLONG_MIN,LLONG_MAX,0,-1,1};
    for (int t=0;t<30000;t++)
    {
        int k=rng()%4,op=rng()%10;
        long long v=rng()%4==0 ? edges[rng()%edges.size()] : (long long)(rng()%200001)-100000;
        if (op<4 || handle.empty())
        {
            int id=handle.size();
            handle.push_back(q[k].push({v,id}));
            owner.push_back(k);value.push_back(v);ref[k].insert({v,id});
        }
        else if (op<6)
        {
            int id=rng()%handle.size();
            if (owner[id]>=0)
            {
                k=owner[id];ref[k].erase({value[id],id});
                q[k].modify(handle[id],{v,id});value[id]=v;ref[k].insert({v,id});
                assert(*handle[id]==P(v,id));
            }
        }
        else if (op==6)
        {
            int id=rng()%handle.size();
            if (owner[id]>=0) { q[owner[id]].erase(handle[id]);forget(id); }
        }
        else if (op==7)
        {
            if (!q[k].empty()) { int id=q[k].top().second;q[k].pop();forget(id); }
        }
        else
        {
            int j=(k+1+rng()%3)%4;
            if (op==8)
            {
                q[k].join(q[j]);assert(q[j].empty());
                for (auto x:ref[j]) { owner[x.second]=k;ref[k].insert(x); }
                ref[j].clear();
            }
            else
            {
                q[k].swap(q[j]);ref[k].swap(ref[j]);
                for (auto x:ref[k]) owner[x.second]=k;
                for (auto x:ref[j]) owner[x.second]=j;
            }
        }
        for (int i=0;i<4;i++)
        {
            assert(q[i].size()==ref[i].size());
            assert(q[i].empty()==ref[i].empty());
            if (!q[i].empty()) assert(q[i].top()==*ref[i].rbegin());
        }
    }
    for (int id=0;id<(int)handle.size();id++)
        if (owner[id]>=0) assert(*handle[id]==P(value[id],id));
    auto copied=q[0];
    while (!copied.empty())
    {
        assert(copied.top()==*ref[0].rbegin());
        ref[0].erase(prev(ref[0].end()));copied.pop();
    }
    for (int id=0;id<(int)owner.size();id++)
        if (owner[id]==0) assert(*handle[id]==P(value[id],id));
    pheap<int,greater<int>> lo,part;
    auto a=lo.push(7),b=lo.push(2),c=lo.push(9);
    lo.modify(a,-3);assert(lo.top()==-3);
    lo.split([](int x){return x%2==0;},part);
    assert(part.top()==2 && *b==2);
    part.modify(b,-5);lo.join(part);
    assert(part.empty() && lo.top()==-5 && *a==-3 && *c==9);
    lo.erase(b);lo.pop();assert(lo.top()==9);
    lo.clear();assert(lo.empty());
    pheap<pair<int,int>,greater<pair<int,int>>> large;
    vector<decltype(large)::point_iterator> h;
    for (int i=0;i<200000;i++) h.push_back(large.push({i,i}));
    for (int i=0;i<200000;i++) large.modify(h[i],{-i,i});
    for (int i=199999;i>=0;i--) { assert(large.top()==make_pair(-i,i));large.pop(); }
    cout << "PBDS pairing heap: ordered-set oracle, handle ownership after join/swap/split, copy isolation and 200000 modifications PASS\n";
}
