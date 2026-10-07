#include "../src/compact/adaptive_simpson.hpp"

int kind;
vector<long double> coef;
int calls;

template<class T>
T eval(T x)
{
    if (kind == 1)
        return 1 / (1 + x * x);
    if (kind == 2)
        return exp(x);
    if (kind == 3)
        return sin(x);
    if (kind == 4)
    {
        T y = 1;
        for (int i = 0; i < 5; i++)
            y *= x - T(i) / 4;
        return y * y;
    }
    T y = 0;
    for (int i = (int)coef.size() - 1; i >= 0; i--)
        y = y * x + T(coef[i]);
    return y;
}

double F(double x)
{
    calls++;
    return eval(x);
}

#include "fixtures/simpson_sources/kuangbin.inc"

int main()
{
    cout << setprecision(24);
    int degree;
    double a, b, eps;
    while (cin >> kind >> a >> b >> eps >> degree)
    {
        coef.resize(degree + 1);
        for (auto &x : coef)
            cin >> x;
        calls = 0;
        double old = asr(a, b, eps);
        int old_calls = calls;
        calls = 0;
        auto f = [](long double x)
        {
            calls++;
            return eval(x);
        };
        auto now = AdaptiveSimpson::integrate(f, a, b, eps);
        cout << old << ' ' << old_calls << ' ' << now.value << ' '
             << now.error << ' ' << now.met << ' ' << now.evaluations
             << ' ' << calls << '\n';
    }
}
