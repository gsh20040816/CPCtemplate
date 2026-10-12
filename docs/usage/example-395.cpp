int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long a, b;
    cin >> a >> b;
    auto left = digit_count(a - 1);
    auto right = digit_count(b);
    for (int d = 0; d < 10; d++)
        cout << (long long)(right[d] - left[d]) << " \n"[d == 9];
}
