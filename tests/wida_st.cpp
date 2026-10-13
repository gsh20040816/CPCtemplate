#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_st/main.cpp"

int main()
{
    ST st(8);
    for (int i = 1; i <= 8; i++) {
        st.in1[i] = (i * 3) % 11;
        st.in2[i] = 20 - i * 2;
    }
    st.init();
    for (int l = 1; l <= 8; l++) for (int r = 1; r <= 8; r++) {
        int a = min(l, r), b = max(l, r), mx = st.in1[a], mn = st.in2[a];
        for (int i = a; i <= b; i++) {
            mx = max(mx, st.in1[i]);
            mn = min(mn, st.in2[i]);
        }
        if (st.getMax(l, r) != mx || st.getMin(l, r) != mn) return 1;
    }
    ST one(1);
    one.in1[1] = 7;
    one.in2[1] = -4;
    one.init();
    cout << one.getMax(1, 1) << ' ' << one.getMin(1, 1) << '\n';
}
