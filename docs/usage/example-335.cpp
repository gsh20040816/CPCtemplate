int main()
{
    unsigned long long m;
    cin >> m;
    FibonacciPeriod solver;
    cout << (unsigned long long)solver.period(m) << '\n';
    return 0;
}
