#include <iostream>
#include "../../src/compact/general_sam.hpp"
#include "../../src/compact/sam_queries.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    GeneralSAM sam;
    for (int i = 0; i < n; i++)
    {
        string s;
        cin >> s;
        sam.add(s);
    }
    sam.build();
    string alphabet, t;
    long long k;
    cin >> alphabet >> k >> t;
    SAMLex index(sam);
    auto ans = index.kth(k, alphabet);
    cout << (ans ? *ans : "-1") << '\n';
    auto [start, length] = sam_lcs(sam, t);
    cout << start << ' ' << length << '\n';
}
