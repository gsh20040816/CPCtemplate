int main()
{
    int tests;
    cin >> tests;
    FibonacciPeriod solver;
    for (int i = 1; i <= tests; i++)
    {
        int m;
        cin >> m;
        cout << "Case #" << i << ": ";
        cout << (unsigned long long)solver.period(m) << '\n';
    }
    return 0;
}
