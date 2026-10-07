int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    FibonacciPeriod solver;
    while (tests--)
    {
        unsigned long long m;
        cin >> m;
        auto answer = solver.period(m);
        string output;
        do
        {
            output.push_back('0' + answer % 10);
            answer /= 10;
        }
        while (answer);
        reverse(output.begin(), output.end());
        cout << output << '\n';
    }
    return 0;
}
