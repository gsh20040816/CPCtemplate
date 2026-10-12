int main()
{
    string s, t;
    cin >> s >> t;
    BigInteger a(s), b(t);
    cout << (a * b).str() << '\n';
}
