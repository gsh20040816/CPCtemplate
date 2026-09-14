int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    cin >> s;
    int n = s.size();
    auto [odd, even] = manacher(s);
    vector<int> answer(2 * n - 1);
    for (int i = 0; i < n; i++)
    {
        answer[2 * i] = 2 * odd[i] - 1;
        if (i) answer[2 * i - 1] = 2 * even[i];
    }
    for (int i = 0; i < (int)answer.size(); i++)
        cout << answer[i] << (i + 1 == (int)answer.size() ? '\n' : ' ');
}
