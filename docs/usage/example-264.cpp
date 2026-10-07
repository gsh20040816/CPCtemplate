int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int m;
    cin >> m;
    DynamicAC dict;
    while (m--)
    {
        int t;
        string s;
        cin >> t >> s;
        if (t == 3)
        {
            cout << dict.query(s) << endl;
        }
        else
        {
            dict.add(move(s), t == 1 ? 1 : -1);
        }
    }
}
