int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n;
    std::cin >> n;
    XorBasis basis;
    for (int i = 0; i < n; i++)
    {
        unsigned long long x;
        std::cin >> x;
        basis.insert(x);
    }
    std::cout << basis.query() << '\n';
}
