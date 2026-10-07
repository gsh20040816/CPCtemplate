#include <iostream>
#include "../../src/compact/general_sam.hpp"
#include "../../src/compact/sam_documents.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<string> s(n);
    GeneralSAM sam;
    for (auto &t : s)
    {
        cin >> t;
        sam.add(t);
    }
    sam.build();
    SAMDocuments index(sam, s);
    while (q--)
    {
        string t;
        cin >> t;
        int p = 0;
        for (char c : t)
        {
            p = sam.a[p].go[c - 'a'];
            if (!p) break;
        }
        cout << (p ? index.cnt[p] : 0) << '\n';
    }
}
