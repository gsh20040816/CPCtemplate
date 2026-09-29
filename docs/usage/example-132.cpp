int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    GeneralSAM sam;
    while (n--)
    {
        string s;
        cin >> s;
        sam.add(s);
    }
    sam.build();
    cout << sam.distinct() << '\n' << sam.a.size() << '\n';
}
