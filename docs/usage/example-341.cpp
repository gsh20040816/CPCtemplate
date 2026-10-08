int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    cin >> s;
    DC3 d(s);
    for (int i = 0; i < (int)d.sa.size(); i++)
        cout << d.sa[i] << (i + 1 == (int)d.sa.size() ? '\n' : ' ');
    return 0;
}
