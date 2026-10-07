#include "../src/compact/fenwick2d.hpp"
#include "../src/compact/rectangle_fenwick.hpp"
#include <climits>
#include <iostream>
#include <map>
#include <random>
#include <stdexcept>
#include <string>

using ll = long long;
using I = __int128_t;
long long cases = 0, checks = 0;
std::mt19937 rng(45142026);

void require(bool ok)
{
    checks++;
    if (!ok) throw std::runtime_error("oracle mismatch");
}

void sparse()
{
    std::vector<ll> c{LLONG_MIN, -9, -1, 0, 1, 7, LLONG_MAX - 1};
    std::vector<ll> ends = c;
    ends.push_back(LLONG_MAX);
    for (int repeat = 0; repeat < 150; repeat++)
    {
        cases++;
        std::vector<std::pair<ll,ll>> p;
        std::map<std::pair<ll,ll>, I> w;
        for (ll x : c)
            for (ll y : c)
                if (rng() % 3 == 0)
                {
                    p.push_back({x,y});
                    if (rng() % 2) p.push_back({x,y});
                    w[{x,y}] = 0;
                }
        std::shuffle(p.begin(), p.end(), rng);
        Fenwick2D<I> tree(p);
        auto fresh = tree;
        for (ll x : ends)
            for (ll y : ends) require(fresh.prefix(x,y) == 0);
        for (int step = 0; step < 150; step++)
        {
            if (!p.empty())
            {
                auto [x,y] = p[rng() % p.size()];
                I v = (I)((int)(rng() % 19) - 9) * (I(1) << 70);
                tree.add(x,y,v);
                w[{x,y}] += v;
            }
            for (ll x : ends)
                for (ll y : ends)
                {
                    I want = 0;
                    for (auto [xy,v] : w)
                        if (xy.first < x && xy.second < y) want += v;
                    require(tree.prefix(x,y) == want);
                }
            for (int t = 0; t < 10; t++)
            {
                ll l = ends[rng()%ends.size()], r = ends[rng()%ends.size()];
                ll d = ends[rng()%ends.size()], u = ends[rng()%ends.size()];
                if (l > r) std::swap(l,r);
                if (d > u) std::swap(d,u);
                I want = 0;
                for (auto [xy,v] : w)
                    if (l <= xy.first && xy.first < r && d <= xy.second && xy.second < u)
                        want += v;
                require(tree.sum(l,d,r,u) == want);
            }
            if (step % 25 == 0)
            {
                auto copy = tree;
                require(copy.sum(LLONG_MIN,LLONG_MIN,LLONG_MAX,LLONG_MAX)
                    == tree.sum(LLONG_MIN,LLONG_MIN,LLONG_MAX,LLONG_MAX));
                copy.init({});
                require(copy.sum(LLONG_MIN,LLONG_MIN,LLONG_MAX,LLONG_MAX) == 0);
                require(tree.pt == fresh.pt);
            }
        }
        tree.init(p);
        require(tree.sum(LLONG_MIN,LLONG_MIN,LLONG_MAX,LLONG_MAX) == 0);
    }
    Fenwick2D<> empty;
    require(empty.sum(LLONG_MIN,LLONG_MIN,LLONG_MAX,LLONG_MAX) == 0);
    const int n = 200000;
    std::vector<std::pair<ll,ll>> p;
    for (int i = 0; i < n; i++) p.push_back({i, n-i});
    Fenwick2D tree(p);
    for (int i = 0; i < n; i++) tree.add(i,n-i,1000000000LL);
    for (int i = 0; i <= n; i++)
    {
        require(tree.prefix(i,n+1) == i * 1000000000LL);
        require(tree.sum(0,0,i,n-i+1) == 0);
    }
    for (int i = 0; i < n; i++) tree.add(i,n-i,-1000000000LL);
    require(tree.prefix(n,n+1) == 0);
    cases++;
}

void dense()
{
    for (int n = 0; n <= 6; n++)
        for (int m = 0; m <= 6; m++)
        {
            cases++;
            RectangleFenwick<I> tree(n,m);
            std::vector<std::vector<I>> a(n,std::vector<I>(m));
            auto verify = [&]()
            {
                for (int l = 0; l <= n; l++)
                    for (int r = l; r <= n; r++)
                        for (int d = 0; d <= m; d++)
                            for (int u = d; u <= m; u++)
                            {
                                I want = 0;
                                for (int i = l; i < r; i++)
                                    for (int j = d; j < u; j++) want += a[i][j];
                                require(tree.sum(l,d,r,u) == want);
                            }
            };
            verify();
            for (int step = 0; step < 120; step++)
            {
                int l=rng()%(n+1), r=rng()%(n+1);
                int d=rng()%(m+1), u=rng()%(m+1);
                if (l > r) std::swap(l,r);
                if (d > u) std::swap(d,u);
                I v = (I)((int)(rng()%19)-9) * (I(1)<<70);
                tree.add(l,d,r,u,v);
                for (int i=l; i<r; i++)
                    for (int j=d; j<u; j++) a[i][j]+=v;
                verify();
                if (step % 25 == 0)
                {
                    auto copy=tree;
                    require(copy.sum(0,0,n,m)==tree.sum(0,0,n,m));
                    copy.add(0,0,n,m,13);
                    require(copy.sum(0,0,n,m)==tree.sum(0,0,n,m)+I(n)*m*13);
                    verify();
                }
            }
            tree=RectangleFenwick<I>(n,m);
            require(tree.sum(0,0,n,m)==0);
        }
    const int n=2048;
    RectangleFenwick<ll> tree(n,n);
    tree.add(0,0,n,n,500);
    // Cancellation in four moments is tested at nonzero near-end origins.
    tree.add(n-5,n-7,n,n,-499);
    for (int x=0; x<=n; x++)
        for (int t=0; t<4; t++)
        {
            int y=rng()%(n+1);
            ll want=500LL*x*y-499LL*std::max(0,x-n+5)*std::max(0,y-n+7);
            require(tree.prefix(x,y)==want);
        }
    tree.add(0,0,n,n,-500);
    tree.add(n-5,n-7,n,n,499);
    require(tree.sum(0,0,n,n)==0);
    cases++;
}

int main(int argc, char **argv)
{
    if (argc > 1 && std::string(argv[1]) == "invalid")
    {
        Fenwick2D tree({{0,7},{1,9}});
        tree.add(1,7,1LL);
        return 0;
    }
    try
    {
        sparse();
        dense();
        std::cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const std::runtime_error &)
    {
        std::cout << "ORACLE_REJECT\n";
    }
}
