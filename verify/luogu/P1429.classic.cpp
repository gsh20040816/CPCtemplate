#include "../../src/classic/closest_pair.hpp"

int main()
{
    int n;
    scanf("%d", &n);
    vector<Closest_Pair::Point> p(n);
    for ( auto &v : p )
        scanf("%Lf%Lf", &v.x, &v.y);
    printf("%.4Lf\n", *Closest_Pair::Solve(p));
}
