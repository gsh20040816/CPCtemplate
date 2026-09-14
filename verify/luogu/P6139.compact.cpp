#include "../../src/compact/general_sam.hpp"
#include <iostream>
using namespace std;

// Candidate only: the second output follows endpos-class GSAM state count.
// Its distinction from the statement's minimal suffix DFA is recorded separately.
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    GeneralSAM sam;
    while (n--)
    {
        string s;
        cin >> s;
        sam.add(s);
    }
    sam.build();
    cout << sam.distinct() << '\n' << sam.a.size() << '\n';
}
