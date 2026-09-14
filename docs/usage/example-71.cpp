int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    cin >> s;
    SuffixAutomaton sam;
    for (char c : s) sam.extend(c - 'a');
    cout << sam.distinct() << '\n';
}
