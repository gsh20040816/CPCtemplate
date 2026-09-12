#include "../src/classic/determinant_mod.hpp"
#include "../src/compact/determinant_mod.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using B=boost::multiprecision::cpp_int;
using L=long long;
using Matrix=vector<vector<L>>;
B permutation(const Matrix &a)
{
    int n=a.size();
    vector<int> p(n);
    iota(p.begin(),p.end(),0);
    B answer=0;
    do
    {
        B term=1;
        int sign=0;
        for(int i=0;i<n;i++)
        {
            term*=a[i][p[i]];
            for(int j=0;j<i;j++) sign^=p[j]>p[i];
        }
        answer+=sign?-term:term;
    }while(next_permutation(p.begin(),p.end()));
    return answer;
}
B bareiss(Matrix input)
{
    int n=input.size();
    if(!n) return 1;
    vector<vector<B>> a(n,vector<B>(n));
    for(int i=0;i<n;i++) for(int j=0;j<n;j++) a[i][j]=input[i][j];
    B previous=1;
    int sign=1;
    for(int k=0;k<n-1;k++)
    {
        int p=k;
        while(p<n && a[p][k]==0) p++;
        if(p==n) return 0;
        if(p!=k)
        {
            swap(a[p],a[k]);
            sign=-sign;
        }
        B pivot=a[k][k];
        for(int i=k+1;i<n;i++)
        {
            for(int j=k+1;j<n;j++)
            {
                B numerator=a[i][j]*pivot-a[i][k]*a[k][j];
                assert(numerator%previous==0);
                a[i][j]=numerator/previous;
            }
            a[i][k]=0;
        }
        previous=pivot;
    }
    return sign*a[n-1][n-1];
}
void check(const Matrix &a,L mod,B expected)
{
    B want=expected%mod;
    if(want<0) want+=mod;
    L x=determinant_mod(a,mod),y=Determinant_Mod(a,mod);
    assert(x==y && x==want.convert_to<L>());
}
int main()
{
    for(int code=0;code<19683;code++)
    {
        int x=code;
        Matrix a(3,vector<L>(3));
        for(auto &r:a) for(auto &v:r)
        {
            v=x%3-1;
            x/=3;
        }
        B want=permutation(a);
        check(a,4,want);
        check(a,6,want);
    }
    mt19937_64 rng(20260921);
    vector<L> mods{1,2,8,9,1000000006,LLONG_MAX};
    for(int t=0;t<600;t++)
    {
        int n=rng()%9;
        Matrix a(n,vector<L>(n));
        for(auto &row:a) for(auto &v:row)
        {
            switch(rng()%5)
            {
                case 0: v=LLONG_MIN; break;
                case 1: v=LLONG_MAX; break;
                default: v=L(rng()%2001)-1000;
            }
        }
        B want=bareiss(a);
        if(n<=4) assert(want==permutation(a));
        for(L mod:mods) check(a,mod,want);
    }
    Matrix fibonacci{{7540113804746346429LL,1},{4660046610375530309LL,0}};
    check(fibonacci,LLONG_MAX,permutation(fibonacci));
    Matrix diagonal(300,vector<L>(300));
    B product=1;
    for(int i=0;i<300;i++)
    {
        diagonal[i][i]=LLONG_MAX-1-i;
        product*=diagonal[i][i];
    }
    check(diagonal,LLONG_MAX,product);
    reverse(diagonal.begin(),diagonal.end());
    check(diagonal,1000000006,product); // 300*299/2 is even.
    int n=150;
    Matrix lap(n-1,vector<L>(n-1,-1));
    for(int i=0;i<n-1;i++) lap[i][i]=n-1;
    B trees=1;
    for(int i=0;i<n-2;i++) trees*=n;
    check(lap,1000000006,trees);
    cout<<"Arbitrary-mod determinant dual permutation/Bareiss oracles, composite nonunits, signed64 extremes and large diagonal/Cayley matrices PASS\n";
}
