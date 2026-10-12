int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, k, nested;
    cin >> n >> m >> k >> nested;
    vector<string> a(n);
    for (auto &row : a) cin >> row;
    using Count = boost::multiprecision::cpp_int;
    cout << grid_cycles<Count>(a, k, nested != 0) << '\n';
}
