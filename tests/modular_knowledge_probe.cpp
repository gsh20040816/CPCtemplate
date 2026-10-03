#include "../src/compact/mod_inverse.hpp"
#include "../src/compact/linear_congruence.hpp"
#include "../src/compact/crt_merge.hpp"
#include "../src/compact/euler_power.hpp"
#include "../src/compact/lucas.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    char op;
    while (cin >> op)
    {
        if (op == 'I')
        {
            long long a, m;
            cin >> a >> m;
            cout << mod_inverse(a, m) << '\n';
        }
        else if (op == 'C')
        {
            long long a, b, m;
            cin >> a >> b >> m;
            auto [x, period] = linear_congruence(a, b, m);
            cout << x << ' ' << period << '\n';
        }
        else if (op == 'R')
        {
            long long r, m, a, n;
            cin >> r >> m >> a >> n;
            if (!crt_merge(r, m, a, n)) cout << -1 << '\n';
            else cout << r << ' ' << m << '\n';
        }
        else if (op == 'E')
        {
            unsigned long long a, m, phi;
            string b;
            cin >> a >> b >> m >> phi;
            cout << euler_power(a, b, m, phi) << '\n';
        }
        else
        {
            int p;
            unsigned long long n, k;
            cin >> p >> n >> k;
            cout << Lucas(p).choose(n, k) << '\n';
        }
    }
}
