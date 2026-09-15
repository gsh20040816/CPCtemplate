int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<string> a(n);
    for (auto &row : a) cin >> row;
    auto b = matrix_inverse_mod2(a);
    if (!b)
        cout << -1 << '\n';
    else
        for (auto &row : *b) cout << row << '\n';
}
