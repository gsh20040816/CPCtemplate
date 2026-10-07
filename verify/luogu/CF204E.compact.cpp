#include <iostream>
#include "../../src/compact/general_sam.hpp"
#include "../../src/compact/sam_documents.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k;
    cin >> n >> k;
    vector<string> s(n);
    GeneralSAM sam;
    for (auto &t : s)
    {
        cin >> t;
        sam.add(t);
    }
    sam.build();
    SAMDocuments index(sam, s);
    auto best = index.lengths(k);
    for (int id = 0; id < n; id++)
    {
        int p = 0;
        long long ans = 0;
        for (char c : s[id])
        {
            p = sam.a[p].go[c - 'a'];
            ans += best[p];
        }
        cout << ans << (id + 1 == n ? '\n' : ' ');
    }
}
