#include <bits/stdc++.h>
using namespace std;

int main()
{
    string line;
    while (getline(cin, line))
    {
        istringstream in(line);
        vector<long long> a;
        bool ok = true;
        while (in >> ws && !in.eof())
        {
            long long x;
            if (!(in >> x))
            {
                ok = false;
                break;
            }
            int c = in.peek();
            if (c != char_traits<char>::eof() && !isspace(c))
            {
                ok = false;
                break;
            }
            a.push_back(x);
        }
        if (!ok)
        {
            cout << "invalid\n";
            continue;
        }
        cout << a.size();
        for (long long x : a)
            cout << ' ' << x;
        cout << '\n';
    }
}
