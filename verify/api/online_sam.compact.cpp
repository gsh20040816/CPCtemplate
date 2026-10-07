#include <iostream>
#include "../../src/compact/online_sam.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q;
    cin >> q;
    OnlineSAM sam;
    vector<int> state(q + 1);
    for (int i = 1; i <= q; i++)
    {
        int parent;
        char c;
        cin >> parent >> c;
        state[i] = sam.extend(state[parent], c - 'a');
        cout << sam.total << '\n';
    }
}
