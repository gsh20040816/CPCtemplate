#include "../src/compact/adaptive_simpson.hpp"

int main(int argc, char **)
{
    if (argc > 1)
    {
        try
        {
            AdaptiveSimpson::integrate([](long double) -> long double
            {
                throw 7;
            }, 0, 1, 1e-6L);
        }
        catch (int x)
        {
            cout << x << '\n';
            return 0;
        }
        return 1;
    }
    cout << setprecision(numeric_limits<long double>::max_digits10);
    int n;
    cin >> n;
    while (n--)
    {
        int kind, degree, depth, limit;
        long double a, b, eps;
        cin >> kind >> a >> b >> eps >> depth >> limit >> degree;
        vector<long double> c(degree + 1);
        for (auto &x : c) cin >> x;
        if (kind == 9) b = nextafter(a, b);
        if (kind == 10) b = nextafter(nextafter(a, b), b);
        if (kind == 11) a = numeric_limits<long double>::quiet_NaN();
        if (kind == 12) eps = numeric_limits<long double>::infinity();
        if (kind == 13) eps = numeric_limits<long double>::denorm_min();
        if (kind == 15) eps = 3 * numeric_limits<long double>::denorm_min();
        int calls = 0;
        set<long double> samples;
        auto f = [&](long double x)
        {
            calls++;
            samples.insert(x);
            if (kind == 1) return 1 / (1 + x * x);
            if (kind == 2) return exp(x);
            if (kind == 3) return sin(x);
            if (kind == 4) return exp(-x * x);
            if (kind == 5)
            {
                long double p = 1;
                for (int i = 0; i < 5; i++) p *= x - i / 4.0L;
                return p * p;
            }
            if (kind == 6 && x == 0.5L)
                return numeric_limits<long double>::quiet_NaN();
            if (kind == 7 && x == 0.25L)
                return numeric_limits<long double>::infinity();
            if (kind == 8) return numeric_limits<long double>::max() / 2;
            if (kind == 14)
            {
                int k = int(x / 2);
                if (k % 2) return numeric_limits<long double>::max() / 8;
                return k == 2 || k == 6 ? 1.0L : 0.0L;
            }
            if (kind == 15)
            {
                int values[] = {0, 22, 20, 23, 0, 22, 20, 23, 0};
                return values[int(x / 1.5L)] *
                       numeric_limits<long double>::denorm_min();
            }
            long double value = 0;
            for (int i = degree; i >= 0; i--) value = value * x + c[i];
            return value;
        };
        auto r = AdaptiveSimpson::integrate(f, a, b, eps, depth, limit);
        cout << r.met << ' ' << r.value << ' ' << r.error << ' '
             << r.evaluations << ' ' << calls << ' ' << samples.size() << ' '
             << a << ' ' << b << ' ' << eps << '\n';
    }
}
