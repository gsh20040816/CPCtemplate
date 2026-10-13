#include <bits/stdc++.h>
#undef getc
#include "fixtures/wida_fread/main.cpp"

int main(int argc, char **argv)
{
    std::string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "empty") {
        int a;
        QuickRead::Cin(a);
        return 0;
    }
    if (mode == "big") {
        int a;
        QuickRead::Cin(a);
        std::cout << a << '\n';
        return 0;
    }
    if (mode == "min") {
        QuickRead::write(INT_MIN);
        return 0;
    }
    int a, b, c;
    QuickRead::Cin(a, b, c);
    QuickRead::write(a);
    putchar(' ');
    QuickRead::write(b);
    putchar(' ');
    QuickRead::write(c);
    putchar('\n');
}
