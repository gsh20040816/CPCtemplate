#include "../../src/compact/convolution_mod.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    const int mod = 1000003;
    using Z = ModInt<mod>;
    int n, b, c, d;
    while (cin >> n >> b >> c >> d)
    {
        assert(1 <= n && n <= 100010);
        vector<Z> a(n);
        for (Z &v : a)
        {
            int x;
            cin >> x;
            v = x;
        }
        Z base = b, ratio = c, shift = d;
        if (ratio.v == 0)
        {
            Z first = 0, rest = 0;
            for (int i = n - 1; i >= 0; i--)
            {
                first = first * (base + shift) + a[i];
                rest = rest * shift + a[i];
            }
            cout << first.v << '\n';
            for (int i = 1; i < n; i++)
                cout << rest.v << '\n';
            continue;
        }
        vector<Z> fact(n, 1), inv(n, 1);
        for (int i = 1; i < n; i++)
            fact[i] = fact[i - 1] * Z(i);
        inv[n - 1] = fact[n - 1].inv();
        for (int i = n - 1; i > 0; i--)
            inv[i - 1] = inv[i] * Z(i);
        vector<int> x(n), y(n);
        Z power = 1;
        for (int i = 0; i < n; i++)
        {
            x[n - 1 - i] = (a[i] * fact[i]).v;
            y[i] = (power * inv[i]).v;
            power = power * shift;
        }
        auto product = convolution_mod(x, y, mod);
        power = 1;
        for (int j = 0; j < n; j++)
        {
            a[j] = Z(product[n - 1 - j]) * inv[j] * power;
            power = power * base;
        }
        vector<Z> square(n, 1), inverse(n, 1);
        Z step = ratio, backward = ratio.inv();
        Z step2 = step * step, backward2 = backward * backward;
        for (int i = 1; i < n; i++)
        {
            square[i] = square[i - 1] * step;
            inverse[i] = inverse[i - 1] * backward;
            step = step * step2;
            backward = backward * backward2;
        }
        y.resize(2 * n - 1);
        for (int j = 0; j < n; j++)
        {
            x[j] = (a[j] * square[j]).v;
            y[n - 1 - j] = inverse[j].v;
            y[n - 1 + j] = inverse[j].v;
        }
        product = convolution_mod(x, y, mod);
        for (int k = 0; k < n; k++)
            cout << (square[k] * Z(product[n - 1 + k])).v << '\n';
    }
    return 0;
}
