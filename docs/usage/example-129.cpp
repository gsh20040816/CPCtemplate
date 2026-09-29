int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    cin >> s;
    auto [odd, even] = manacher(s);
    int answer = 0;
    for (int i = 0; i < (int)s.size(); i++)
    {
        answer = max(answer, 2 * odd[i] - 1);
        answer = max(answer, 2 * even[i]);
    }
    cout << answer << '\n';
}
