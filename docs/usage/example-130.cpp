int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    cin >> s;
    SuffixAutomaton sam;
    for (char c : s) sam.extend(c - 'a');
    auto count = sam.counts();
    long long answer = 0;
    for (int u = 1; u < (int)sam.a.size(); u++)
    {
        if (count[u] > 1) answer = max(answer, count[u] * sam.a[u].len);
    }
    cout << answer << '\n';
}
