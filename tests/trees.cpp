#include "../src/classic/dynamic_tree.hpp"
#include "../src/classic/splay.hpp"
#include "../src/classic/treap.hpp"
#include "../src/compact/dynamic_tree.hpp"
#include "../src/compact/splay.hpp"
#include "../src/compact/treap.hpp"
#include <algorithm>
#include <climits>
#include <iostream>
#include <numeric>
#include <queue>

using U = unsigned long long;
std::mt19937_64 random_engine(20260920);

int random_int(int n) { return random_engine() % n; }

std::vector<int> forest_path(const std::vector<std::vector<int>> &edge, int s,
                             int t) {
  int n = edge.size() - 1;
  std::vector<int> parent(n + 1), q{s};
  parent[s] = s;
  for (int i = 0; i < (int)q.size(); i++) {
    int u = q[i];
    for (int v = 1; v <= n; v++) {
      if (!edge[u][v] || parent[v])
        continue;
      parent[v] = u;
      q.push_back(v);
    }
  }
  if (!parent[t])
    return {};
  std::vector<int> answer{t};
  while (t != s) {
    t = parent[t];
    answer.push_back(t);
  }
  return answer;
}

void dynamic_forest() {
  static Link_Cut_Tree<32> b;
  for (int test = 0; test < 300; test++) {
    int n = 1 + random_int(30);
    LinkCutTree a(n);
    b.Init(n);
    std::vector<std::vector<int>> edge(n + 1, std::vector<int>(n + 1));
    std::vector<U> value(n + 1);
    for (int i = 1; i <= n; i++) {
      value[i] = random_engine();
      a.set(i, value[i]);
      b.Set(i, value[i]);
    }
    for (int step = 0; step < 500; step++) {
      int x = 1 + random_int(n), y = 1 + random_int(n);
      auto path = forest_path(edge, x, y);
      bool connected = !path.empty();
      int op = random_int(6);
      if (op == 0) {
        assert(a.link(x, y) == !connected);
        assert(b.Link(x, y) == !connected);
        if (!connected)
          edge[x][y] = edge[y][x] = 1;
      } else if (op == 1) {
        bool present = edge[x][y];
        assert(a.cut(x, y) == present);
        assert(b.Cut(x, y) == present);
        edge[x][y] = edge[y][x] = 0;
      } else if (op == 2) {
        value[x] = random_engine();
        a.set(x, value[x]);
        b.Set(x, value[x]);
      } else if (op == 3 && connected) {
        U expected = 0;
        for (int v : path)
          expected ^= value[v];
        assert(a.query(x, y) == expected);
        assert(b.Query(x, y) == expected);
        assert(a.query(y, x) == expected);
        assert(b.Query(y, x) == expected);
      } else if (op == 4) {
        a.make_root(x);
        b.Make_Root(x);
        assert(a.find_root(x) == x);
        assert(b.Find_Root(x) == x);
        if (connected) {
          assert(a.find_root(y) == x);
          assert(b.Find_Root(y) == x);
        }
      } else {
        assert(a.connected(x, y) == connected);
        assert(b.Connected(x, y) == connected);
      }
      if (step % 50 == 0) {
        for (int v = 1; v <= n; v++) {
          assert(a.query(v, v) == value[v]);
          assert(b.Query(v, v) == value[v]);
          bool expected = !forest_path(edge, x, v).empty();
          assert(a.connected(x, v) == expected);
          assert(b.Connected(x, v) == expected);
        }
      }
    }
  }
}

void long_chain() {
  const int n = 200000;
  LinkCutTree a(n);
  static Link_Cut_Tree<n> b;
  b.Init(n);
  U expected = 0;
  for (int i = 1; i <= n; i++) {
    U value = U(i) * 98765432101234567ULL;
    a.set(i, value);
    b.Set(i, value);
    expected ^= value;
    if (i > 1) {
      assert(a.link(i - 1, i));
      assert(b.Link(i - 1, i));
    }
  }
  for (int i = 0; i < 100; i++) {
    assert(a.query(1, n) == expected);
    assert(b.Query(n, 1) == expected);
  }
  assert(a.cut(n / 2, n / 2 + 1));
  assert(b.Cut(n / 2 + 1, n / 2));
  assert(!a.connected(1, n));
  assert(!b.Connected(1, n));
  assert(a.link(1, n));
  assert(b.Link(1, n));
  assert(a.connected(n / 2, n / 2 + 1));
  assert(b.Connected(n / 2, n / 2 + 1));
}

void ordered_set() {
  static Ordered_Treap<600> b;
  for (int test = 0; test < 300; test++) {
    OrderedTreap a(1000 + test);
    OrderedSplay c;
    static Ordered_Splay<600> d;
    d.Init();
    b.Init(9000 + test);
    std::vector<long long> values;
    for (int step = 0; step < 500; step++) {
      long long x = random_int(41) - 20;
      if (step % 31 == 0)
        x = LLONG_MIN;
      if (step % 37 == 0)
        x = LLONG_MAX;
      auto it = std::lower_bound(values.begin(), values.end(), x);
      if (random_int(2)) {
        values.insert(it, x);
        a.insert(x);
        b.Insert(x);
        c.insert(x);
        d.Insert(x);
      } else {
        bool found = it != values.end() && *it == x;
        assert(a.erase(x) == found);
        assert(b.Erase(x) == found);
        assert(c.erase(x) == found);
        assert(d.Erase(x) == found);
        if (found)
          values.erase(it);
      }
      assert(a.size() == (int)values.size());
      assert(b.Size() == (int)values.size());
      assert(c.size() == (int)values.size());
      assert(d.Size() == (int)values.size());
      int lower =
          std::lower_bound(values.begin(), values.end(), x) - values.begin();
      int upper =
          std::upper_bound(values.begin(), values.end(), x) - values.begin();
      assert(a.rank(x) == lower + 1);
      assert(b.Rank(x) == lower + 1);
      assert(c.rank(x) == lower + 1);
      assert(d.Rank(x) == lower + 1);
      assert(a.less(x, true) == upper);
      assert(b.Count_Less(x, true) == upper);
      std::optional<long long> prev, next;
      if (lower)
        prev = values[lower - 1];
      if (upper < (int)values.size())
        next = values[upper];
      assert(a.prev(x) == prev);
      assert(b.Predecessor(x) == prev);
      assert(c.prev(x) == prev);
      assert(d.Predecessor(x) == prev);
      assert(a.next(x) == next);
      assert(b.Successor(x) == next);
      assert(c.next(x) == next);
      assert(d.Successor(x) == next);
      if (!values.empty()) {
        int k = 1 + random_int(values.size());
        assert(a.kth(k) == values[k - 1]);
        assert(b.Kth(k) == values[k - 1]);
        assert(c.kth(k) == values[k - 1]);
        assert(d.Kth(k) == values[k - 1]);
      }
      if (step % 50 == 0) {
        for (int i = 0; i < (int)values.size(); i++) {
          assert(a.kth(i + 1) == values[i]);
          assert(b.Kth(i + 1) == values[i]);
          assert(c.kth(i + 1) == values[i]);
          assert(d.Kth(i + 1) == values[i]);
        }
      }
    }
  }
}

void sequence() {
  static Sequence_Treap<600> b;
  for (int test = 0; test < 300; test++) {
    SequenceTreap a(2000 + test);
    b.Init(8000 + test);
    std::vector<long long> values;
    for (int step = 0; step < 500; step++) {
      int n = values.size();
      int op = random_int(6);
      if (!n || op == 0) {
        int k = random_int(n + 1);
        long long x = random_int(101) - 50;
        a.insert(k, x);
        b.Insert(k, x);
        values.insert(values.begin() + k, x);
      } else {
        int l = 1 + random_int(n), r = 1 + random_int(n);
        if (l > r)
          std::swap(l, r);
        if (op == 1) {
          a.erase(l, r);
          b.Erase(l, r);
          values.erase(values.begin() + l - 1, values.begin() + r);
        } else if (op == 2) {
          a.reverse(l, r);
          b.Reverse(l, r);
          std::reverse(values.begin() + l - 1, values.begin() + r);
        } else if (op == 3) {
          long long x = random_int(101) - 50;
          a.add(l, r, x);
          b.Add(l, r, x);
          for (int i = l - 1; i < r; i++)
            values[i] += x;
        } else {
          long long sum =
              std::accumulate(values.begin() + l - 1, values.begin() + r, 0LL);
          assert(a.query(l, r) == sum);
          assert(b.Query(l, r) == sum);
        }
      }
      assert(a.size() == (int)values.size());
      assert(b.Size() == (int)values.size());
      if (step % 7 == 0) {
        assert(a.values() == values);
        assert(b.Values() == values);
      }
    }
    assert(a.values() == values);
    assert(b.Values() == values);
  }
}

void sorted_splay() {
  const int n = 100000;
  OrderedSplay a;
  static Ordered_Splay<n> b;
  b.Init();
  for (int i = 1; i <= n; i++) {
    a.insert(i);
    b.Insert(i);
  }
  for (int i = 0; i < 100; i++) {
    assert(a.kth(1) == 1);
    assert(b.Kth(1) == 1);
    assert(a.kth(n) == n);
    assert(b.Kth(n) == n);
  }
  for (int i = 1; i <= n; i++) {
    assert(a.rank(i) == i);
    assert(b.Rank(i) == i);
  }
  for (int i = 1; i <= n; i++) {
    assert(a.erase(i));
    assert(b.Erase(i));
  }
  assert(a.size() == 0);
  assert(b.Size() == 0);
}

int main() {
  dynamic_forest();
  std::cout << "Link-cut forest / BFS oracle PASS\n";
  long_chain();
  std::cout << "Link-cut 200000-vertex chain PASS\n";
  ordered_set();
  sorted_splay();
  std::cout << "Ordered treap and splay / sorted vector oracle PASS\n";
  sequence();
  std::cout << "Sequence treap / vector oracle PASS\n";
}
