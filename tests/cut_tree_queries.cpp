#include "../src/classic/cut_tree_queries.hpp"
#include "../src/compact/cut_tree_queries.hpp"
#include <random>
#include <iostream>

int main()
{
    assert(cut_tree_values(1,{})[0][0]==LLONG_MAX);
    assert(Cut_Tree_Values(1,{})[0][0]==LLONG_MAX);
    mt19937 rng(4891);
    for(int t=0;t<1000;t++)
    {
        int n=2+rng()%20;
        vector<tuple<int,int,long long>> edges;
        vector<vector<long long>> expected(n,vector<long long>(n,-1));
        for(int i=0;i<n;i++)
            expected[i][i]=LLONG_MAX;
        for(int i=1;i<n;i++)
        {
            int p=rng()%i;
            long long w=rng()%10;
            edges.push_back({i,p,w});
            expected[i][p]=expected[p][i]=w;
        }
        shuffle(edges.begin(),edges.end(),rng);
        for(int k=0;k<n;k++)
            for(int i=0;i<n;i++)
                for(int j=0;j<n;j++)
                    expected[i][j]=max(expected[i][j],min(expected[i][k],expected[k][j]));
        assert(cut_tree_values(n,edges)==expected);
        assert(Cut_Tree_Values(n,edges)==expected);
    }
    int n=1200;
    vector<tuple<int,int,long long>> chain;
    for(int i=0;i+1<n;i++)
        chain.push_back({i,i+1,LLONG_MAX-i});
    auto a=cut_tree_values(n,chain);
    auto b=Cut_Tree_Values(n,chain);
    for(int i=0;i<n;i++)
        for(int j=0;j<n;j++)
        {
            long long expected=i==j?LLONG_MAX:LLONG_MAX-(max(i,j)-1);
            assert(a[i][j]==expected && b[i][j]==expected);
        }
    cout << "Cut-tree queries dual Floyd bottleneck oracle, zero weights, diagonal sentinel and 1200-vertex recursive chain PASS\n";
}
