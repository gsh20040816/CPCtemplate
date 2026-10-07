#include "../src/compact/isap.hpp"
namespace residual
{
#include "fixtures/matrix_sap_sources/residual.inc"
}
namespace preserved
{
#include "fixtures/matrix_sap_sources/preserved.inc"
}
#include "fixtures/matrix_sap_sources/current.inc"
using I = __int128_t;
long long checks = 0, cases = 0;
void need(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("ORACLE_REJECT");
}
long long oracle(const Matrix &a, int s, int t)
{
    int n = a.size();
    I best = I(1) << 120;
    for (int mask = 0; mask < (1 << n); mask++)
    {
        if (!(mask >> s & 1) || (mask >> t & 1)) continue;
        I value = 0;
        for (int u = 0; u < n; u++)
            for (int v = 0; v < n; v++)
                if ((mask >> u & 1) && !(mask >> v & 1)) value += a[u][v];
        best = min(best,value);
    }
    return (long long)best;
}
void certificate(const Matrix &a, const Matrix &net, int s, int t, long long f)
{
    int n = a.size();
    vector<I> b(n);
    vector<int> vis(n);
    for (int u = 0; u < n; u++)
        for (int v = 0; v < n; v++)
        {
            need(I(net[u][v]) == -I(net[v][u]));
            need(-I(a[v][u]) <= net[u][v] && net[u][v] <= a[u][v]);
            b[u] += net[u][v];
        }
    for (int u = 0; u < n; u++) need(b[u] == (u == s ? I(f) : u == t ? -I(f) : I(0)));
    function<void(int)> visit = [&](int u)
    {
        vis[u] = 1;
        for (int v = 0; v < n; v++)
            if (I(a[u][v])-net[u][v] > 0 && !vis[v]) visit(v);
    };
    visit(s);
    need(!vis[t]);
    I cut = 0;
    for (int u = 0; u < n; u++)
        for (int v = 0; v < n; v++)
            if (vis[u] && !vis[v]) cut += a[u][v];
    need(cut == f);
}
void check(const Matrix &a, int s, int t, long long want)
{
    cases++;
    int n = a.size();
    for (int u = 0; u < n; u++)
        for (int v = 0; v < n; v++) residual::maze[u][v] = preserved::maze[u][v] = a[u][v];
    auto original = a;
    auto [value,net] = matrix_flow(a,s,t);
    need(a == original && value == want);
    certificate(a,net,s,t,value);
    need(residual::sap(s,t,n) == want);
    need(preserved::sap(s,t,n) == want);
    Matrix rn(n,vector<long long>(n)), pn = rn;
    for (int u = 0; u < n; u++)
        for (int v = 0; v < n; v++)
        {
            rn[u][v] = a[u][v]-residual::maze[u][v];
            pn[u][v] = preserved::flow[u][v];
            need(preserved::maze[u][v] == a[u][v]);
        }
    certificate(a,rn,s,t,want);
    certificate(a,pn,s,t,want);
    need(residual::sap(s,t,n) == 0);
    need(preserved::sap(s,t,n) == want);
    need(matrix_flow(a,s,t).first == want);
    // Source #2 resets flow for a new source/sink; #1 retains residual capacity.
    if (n <= 8)
    {
        long long reverse = oracle(a,t,s);
        need(preserved::sap(t,s,n) == reverse);
        auto [f,back] = matrix_flow(a,t,s);
        need(f == reverse);
        certificate(a,back,t,s,f);
        need(residual::sap(t,s,n) == reverse + want);
    }
}
int main(int argc, char **argv)
{
    if (argc > 1)
    {
        string mode = argv[1];
        if (mode == "residual-gap") return residual::sap(0,1,1100);
        if (mode == "preserved-gap") return preserved::sap(0,1,1100);
        if (mode == "residual-overflow")
        {
            residual::maze[0][1] = residual::maze[1][0] = INT_MAX;
            return residual::sap(0,1,2);
        }
        if (mode == "preserved-overflow")
        {
            for (auto [u,v] : vector<pair<int,int>>{{0,1},{0,2},{1,3},{1,4},{2,3},{3,5},{4,5}})
                preserved::maze[u][v] = 1;
            preserved::maze[3][1] = INT_MAX;
            return preserved::sap(0,5,6);
        }
    }
    try
    {
        for (int mask = 0; mask < 729; mask++)
        {
            Matrix a(3,vector<long long>(3));
            int x = mask;
            for (int u = 0; u < 3; u++)
                for (int v = 0; v < 3; v++)
                    if (u != v)
                    {
                        a[u][v] = x%3;
                        x /= 3;
                    }
            check(a,0,2,oracle(a,0,2));
        }
        mt19937 rng(4161);
        for (int it = 0; it < 800; it++)
        {
            int n = 2+rng()%6, s = rng()%n, t = rng()%n;
            if (s == t) t = (t+1)%n;
            Matrix a(n,vector<long long>(n));
            // Repeated ordered endpoints must add rather than overwrite capacity.
            for (int j = 0; j < 25; j++) a[rng()%n][rng()%n] += rng()%11;
            check(a,s,t,oracle(a,s,t));
        }
        Matrix boundary(1099,vector<long long>(1099));
        boundary[0][1098] = 7;
        boundary[1098][0] = 9;
        check(boundary,0,1098,7);
        Matrix dense(70,vector<long long>(70,3));
        check(dense,0,69,207);
        Matrix huge(2,vector<long long>(2,LLONG_MAX));
        auto [f,net] = matrix_flow(huge,0,1);
        need(f == LLONG_MAX);
        certificate(huge,net,0,1,f);
        need(I(huge[1][0])-net[1][0] == I(LLONG_MAX)*2);
        cout << "PASS " << cases << " matrices " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
