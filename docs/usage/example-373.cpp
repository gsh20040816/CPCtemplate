int main()
{
    int n;
    cin >> n;
    string s(n, '\0');
    for (int i = 0; i < n; i++)
    {
        int x;
        cin >> x;
        s[i] = (char)x;
    }
    auto ends = lyndon(s);
    cout << ends.size() << '\n';
    for (int r : ends)
        cout << r << ' ';
    cout << '\n';
}
