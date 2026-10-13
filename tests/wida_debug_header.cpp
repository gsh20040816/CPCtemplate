#include "fixtures/wida_wida_h/main.h"

int main()
{
    cout << vector<int>{} << '\n';
    cout << vector<int>{7} << '\n';
    cout << vector<int>{1, 2, 3} << '\n';
    cout << pair<int, int>{4, 5} << '\n';
    cout << tuple<int, int, int>{1, 2, 3} << '\n';
    cout << string("ab") << '\n';
    stack<int> s;
    for (int x : {1, 2, 3}) s.push(x);
    cout << s << '\n';
    queue<int> q;
    for (int x : {1, 2, 3}) q.push(x);
    cout << q << '\n';
    priority_queue<int> hi;
    for (int x : {1, 2, 3}) hi.push(x);
    cout << hi << '\n';
    priority_queue<int, vector<int>, greater<int>> lo;
    for (int x : {3, 1, 2}) lo.push(x);
    cout << lo << '\n';
    _(1, 2);
    string loop;
    FOR(i, 1, 3) loop += char('0' + i);
    cout << loop << '\n';
}
