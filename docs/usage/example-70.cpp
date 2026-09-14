int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    AhoCorasick ac;
    vector<int> terminal(n);
    for (int &id : terminal)
    {
        string pattern;
        cin >> pattern;
        id = ac.add(pattern);
    }
    ac.build();
    string text;
    cin >> text;
    auto count = ac.count(text);
    for (int id : terminal) cout << count[id] << '\n';
}
