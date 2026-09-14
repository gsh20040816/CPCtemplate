int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    cin >> s;
    GeneralSAM sam;
    sam.add(s);
    sam.build();
    cout << sam.distinct() << '\n';
}
