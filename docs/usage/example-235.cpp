int main()
{
    long double a, b, eps;
    int depth, limit;
    if (!(cin >> a >> b >> eps >> depth >> limit) ||
        !isfinite(a) || !isfinite(b) || abs(a) > 100 || abs(b) > 100 ||
        !isfinite(eps) || eps <= 0 || depth < 0 || depth > 60 ||
        limit < 0 || limit > 200000)
        return 1;
    auto f = [](long double x) { return 1 / (1 + x * x); };
    auto r = AdaptiveSimpson::integrate(f, a, b, eps, depth, limit);
    if (!r.met) cout << "FAILED\n";
    else cout << setprecision(20) << r.value << '\n';
}
