#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_diameter/main.cpp"

int main()
{
    Tree one(1);
    Tree edge(2);
    edge.add(1, 2);
    Tree path(4);
    path.add(1, 2);
    path.add(2, 3);
    path.add(3, 4);
    Tree star(4);
    star.add(1, 2);
    star.add(1, 3);
    star.add(1, 4);
    Tree forest(4);
    forest.add(1, 2);
    forest.add(3, 4);
    cout << one.getlen(1) << ' ' << edge.getlen(1) << ' ' << path.getlen(1) << ' '
         << star.getlen(2) << ' ' << forest.getlen(1) << ' ' << forest.getlen(3) << '\n';
}
