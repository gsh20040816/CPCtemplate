#include "../../src/compact/word_chain.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n;
        cin >> n;
        vector<string> words(n);
        for (auto &word : words)
            cin >> word;
        auto order = word_chain(words);
        if (!order)
        {
            cout << "***\n";
            continue;
        }
        for (int i = 0; i < n; i++)
        {
            if (i)
                cout << '.';
            cout << words[(*order)[i]];
        }
        cout << '\n';
    }
    return 0;
}
