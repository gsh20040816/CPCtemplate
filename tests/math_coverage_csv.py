#!/usr/bin/env python3
"""Keep the source ledger parseable without changing coverage claims."""
import csv
import io
from pathlib import Path


def read(text):
    rows = list(csv.reader(io.StringIO(text), strict=True))
    if not rows or rows[0] != ['topic', 'url', 'status']:
        raise ValueError('Unexpected mathematics ledger header')
    if any(len(row) != 3 or not all(row) for row in rows[1:]):
        raise ValueError('Every mathematics ledger entry needs exactly three cells')
    return rows


def main():
    if not __debug__:
        raise RuntimeError('CSV checks require Python assertions')
    root = Path(__file__).resolve().parents[1]
    text = (root / 'docs/oi-math-coverage.csv').read_text()
    rows = read(text)
    stream = io.StringIO()
    csv.writer(stream, lineterminator='\n').writerows(rows)
    assert read(stream.getvalue()) == rows
    inverse = next(r for r in rows if r[1] == 'https://oi-wiki.org/math/number-theory/inverse/')
    assert 'batch_inverse, inverse_table, mint and batch_units' in inverse[2]
    assert read('topic,url,status\n示例,https://example.test/,"pending, not AC"\n')[1][2] == 'pending, not AC'
    for malformed in ('topic,url,status\n示例,https://example.test/,pending, not AC\n',
                      'topic,url,status\n示例,https://example.test/\n'):
        try:
            read(malformed)
        except ValueError:
            pass
        else:
            raise AssertionError('Malformed ledger was accepted')
    print(f'Mathematics CSV: {len(rows)-1} entries, exact three-cell parsing and lossless round trip PASS')


if __name__ == '__main__':
    main()
