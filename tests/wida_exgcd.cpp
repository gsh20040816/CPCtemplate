    auto dump = [&](int a, int b, int c) {
        std::ostringstream os;
        auto *old = std::cout.rdbuf(os.rdbuf());
        clac(a, b, c);
        std::cout.rdbuf(old);
        return os.str();
    };
    auto expect = [&](int a, int b, int c) {
        int x = 0, y = 0, d = 0;
        for (int t = 1; t <= std::max(std::abs(a), std::abs(b)); t++)
            if (a % t == 0 && b % t == 0) d = t;
        if (c % d != 0) return std::string("-1\n");
        int minx = -1, miny = -1, maxx = -1, maxy = -1, cnt = 0, min_pos_y = -1;
        for (int xx = 1; xx <= 400; xx++) {
            long long rem = c - 1LL * a * xx;
            if (rem % b) continue;
            long long yy = rem / b;
            if (minx < 0) minx = xx;
            if (yy > 0) {
                cnt++;
                miny = miny < 0 ? (int)yy : std::min(miny, (int)yy);
                maxy = std::max(maxy, (int)yy);
                maxx = xx;
            }
        }
        for (int yy = 1; yy <= 400; yy++) if ((c - 1LL * b * yy) % a == 0) {
            min_pos_y = yy;
            break;
        }
        std::ostringstream os;
        if (cnt) os << cnt << '\n' << minx << '\n' << miny << '\n' << maxx << '\n' << maxy << '\n';
        else os << minx << '\n' << min_pos_y << '\n';
        return os.str();
    };
    int x, y;
    int d = exgcd(35, 15, x, y);
    if (d != 5 || 35LL * x + 15LL * y != d) return 1;
    d = exgcd(-4, 6, x, y);
    if (std::abs(d) != 2 || -4LL * x + 6LL * y != d) return 1;
    if (ceil(5, 2) != 3 || ceil(-5, 2) != -2 || ceil(5, -2) != -2 || ceil(-5, -2) != 3) return 1;
    int bad0 = 0, badp = 0;
    for (int a = 1; a <= 8; a++)
        for (int b = 1; b <= 8; b++)
            for (int c = 0; c <= 20; c++) {
                if (dump(a, b, c) == expect(a, b, c)) continue;
                if (c == 0) bad0++;
                else badp++;
            }
    if (dump(1, 2, 0) != "0\n1\n" || expect(1, 2, 0) != "2\n1\n") return 1;
    if (badp != 0) return 1;
    std::cout << "ok " << exgcd(-4, 6, x, y) << ' ' << bad0 << '\n';
