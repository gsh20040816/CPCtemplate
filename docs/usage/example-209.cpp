int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    string s;
    if (!(cin >> n >> s)) return 0;
    int p = minimum_rotation(s);
    rotate(s.begin(), s.begin() + p, s.end());
    cout << s << '\n';
}
