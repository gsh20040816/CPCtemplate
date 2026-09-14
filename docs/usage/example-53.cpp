int main()
{
    int n;
    scanf("%d", &n);
    auto row = stirling_second_row<167772161>(n, n);
    for (int i = 0; i <= n; i++) printf("%d%c", row[i].v, i == n ? '\n' : ' ');
}
