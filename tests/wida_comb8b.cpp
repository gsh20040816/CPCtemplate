#include <bits/stdc++.h>
using namespace std;
struct Z {
    static constexpr int P = 1000000007;
    int v;
    Z(long long x = 0) : v(int(x % P)) { if (v < 0) v += P; }
    Z operator*(Z o) const { return Z(1LL * v * o.v % P); }
    Z inv() const {
        long long a = v, b = P, x = 1, y = 0;
        while (b) {
            long long t = a / b;
            a -= t * b; swap(a, b);
            x -= t * y; swap(x, y);
        }
        return Z(x);
    }
};
#include "fixtures/wida_comb8b/main.cpp"

int main()
{
    int q;
    cin >> q;
    while (q--)
    {
        int n, m;
        cin >> n >> m;
        cout << comb.binom(n, m).v << '\n';
    }
    cout << comb.fac(10).v << ' ' << comb.inv(1).v << ' ' << comb.inv(0).v << '\n';
    cout << comb.fac(100).v << '\n';
}
