"""P13270 full driver and byte-string API checked against enumerated rotations."""
from compiler_config import CXX
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import os
import platform
import random
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import expand

DRIVER = 'verify/luogu/P13270.compact.cpp'
CORE = 'src/compact/string.hpp'
CORE_HARNESS = r'''
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    while (t--)
    {
        int n;
        cin >> n;
        string s(n, '\0');
        for (char &c : s)
        {
            int x;
            cin >> x;
            c = static_cast<char>(x);
        }
        string before = s;
        int p = minimum_rotation(s);
        assert(s == before);
        cout << p << '\n';
    }
}
'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def minimum(s):
    # Complete independent enumeration, with no Booth/duval/suffix machinery.
    return min((s[i:] + s[:i] for i in range(len(s))), default=s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sanitizer', action='store_true')
    args = ap.parse_args()
    sanitizer = args.sanitizer or os.environ.get('SANITIZE') == '1'
    mode = 'sanitizer' if sanitizer else 'normal'
    out = ROOT / 'build' / ('minimum-rotation-usage-' + mode)
    out.mkdir(parents=True, exist_ok=True)
    inputs = [DRIVER, CORE, 'tests/minimum_rotation_usage.py',
              'tests/compiler_config.py', 'tools/usage_examples.py']
    input_hashes = {name: digest((ROOT / name).read_bytes()) for name in inputs}
    text = (ROOT / DRIVER).read_text()
    start = re.search(r'(?m)^int main\(\)', text).start()
    # Match tools/usage_examples.py exactly, without writing shared registration.
    program = ('#include <bits/stdc++.h>\nusing namespace std;\n'
               + expand(text[:start], (ROOT / DRIVER).parent, set()) + text[start:])
    core_block = (ROOT / CORE).read_text().split('// BEGIN minimum_rotation\n', 1)[1]
    core_block = core_block.split('// END minimum_rotation', 1)[0]
    core_program = '#include <bits/stdc++.h>\nusing namespace std;\n' + core_block + CORE_HARNESS
    flags = ['-std=c++20', '-O2']
    if sanitizer:
        flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined',
                 '-fno-omit-frame-pointer']
    env = os.environ.copy()
    if sanitizer:
        env.setdefault('ASAN_OPTIONS', 'detect_leaks=0')
        env.setdefault('UBSAN_OPTIONS', 'halt_on_error=1:print_stacktrace=1')
    commands = []

    def compile_source(name, source, extra=()):
        cpp, exe = out / (name + '.cpp'), out / name
        cpp.write_text(source)
        command = [CXX, *flags, *extra, str(cpp), '-o', str(exe)]
        subprocess.run(command, check=True)
        commands.append(command)
        return exe

    driver = compile_source('P13270', program)
    pasted_program = ('#include <bits/stdc++.h>\nusing namespace std;\n'
                      + core_block + text[start:])
    pasted = compile_source('pasted-usage', pasted_program)
    counts = {}
    corpus = hashlib.sha256()

    def run(exe, data):
        result = subprocess.run([str(exe)], input=data, capture_output=True,
                                check=True, timeout=120, env=env)
        assert not result.stderr, result.stderr.decode(errors='replace')
        return result.stdout

    def driver_case(s, group, expected=None):
        assert 1 <= len(s) <= 10000000 and all(97 <= c <= 122 for c in s)
        want = minimum(s) if expected is None else expected
        data = str(len(s)).encode() + b'\n' + s + b'\n'
        actual = run(driver, data)
        assert actual == want + b'\n', (group, len(s), actual[:100], want[:100])
        counts[group] = counts.get(group, 0) + 1
        corpus.update(group.encode() + b'\0' + data + b'\0' + want + b'\0')

    canonical = [b'a', b'z', b'baca', b'aaaa', b'babababa', b'zzaz',
                 b'cabaaba', b'zyxwvutsrqponmlkjihgfedcba']
    for s in canonical:
        driver_case(s, 'driver_fixed_legal')
        data = str(len(s)).encode() + b'\n' + s + b'\n'
        assert run(pasted, data) == minimum(s) + b'\n'
    counts['pasted_usage_fixed_legal'] = len(canonical)
    rng = random.Random(1327020261002)
    for _ in range(200):
        alphabet = rng.choice([b'ab', b'abc', b'abcdefghijklmnopqrstuvwxyz'])
        s = bytes(rng.choice(alphabet) for _ in range(rng.randint(1, 100)))
        driver_case(s, 'driver_random_rotation_oracle')
    for s in [b'a' * 999 + b'b', b'b' + b'a' * 999, b'ba' * 500,
              b'ab' * 499 + b'aa']:
        driver_case(s, 'driver_long_common_prefix_oracle')
    # The expected rotations below follow simple structural identities and
    # never invoke the tested algorithm (or any second linear rotation method).
    n = 10000000
    driver_case(b'z' * n, 'maximum_legal_all_equal', b'z' * n)
    driver_case(b'b' * (n - 1) + b'a', 'maximum_legal_last_unique_minimum',
                b'a' + b'b' * (n - 1))
    driver_case(b'ba' * (n // 2), 'maximum_legal_periodic', b'ab' * (n // 2))
    driver_case(b'a' * (n - 2) + b'ba', 'maximum_legal_long_equal_prefix',
                b'a' * (n - 1) + b'b')

    # The API operates on string bytes in unsigned-char order. Embedded NUL,
    # whitespace and bytes >=128 are valid core inputs, not P13270 input cases.
    groups = []
    groups.append(('core_empty_extension', [b'']))
    exhaustive = [bytes(v) for n in range(1, 8)
                  for v in itertools.product([0, 127, 255], repeat=n)]
    groups.append(('core_exhaustive_byte_rotation_oracle', exhaustive))
    groups.append(('core_byte_boundaries', [bytes([x]) for x in range(256)]))
    groups.append(('core_fixed_binary', [bytes(range(256)), bytes(range(255, -1, -1)),
                   b'\xff\x80\x00\xff\x80\x00', b'\x80\x7f\x80\x7f',
                   b' \t\n\x00\r\xff', bytes([0]) * 1000,
                   bytes([255]) * 1000, b'\x00' * 999 + b'\xff']))
    groups.append(('core_random_bytes', [bytes(rng.randrange(256)
                   for _ in range(rng.randrange(1, 101))) for _ in range(400)]))
    byte_cases = [(group, s, minimum(s)) for group, values in groups for s in values]
    data = str(len(byte_cases)).encode() + b'\n'
    data += b''.join((str(len(s)) + ' ' + ' '.join(map(str, s)) + '\n').encode()
                     for _, s, _ in byte_cases)
    for group, values in groups:
        counts[group] = len(values)
    corpus.update(data)
    for char_mode in ['signed', 'unsigned']:
        exe = compile_source('core-' + char_mode, core_program, ['-f' + char_mode + '-char'])
        answer = run(exe, data).splitlines()
        assert len(answer) == len(byte_cases)
        for line, (group, s, want) in zip(answer, byte_cases):
            p = int(line)
            if not s:
                assert p == 0
            else:
                assert 0 <= p < len(s), (char_mode, group, s, p)
                assert s[p:] + s[:p] == want, (char_mode, group, s, p, want)
    after = {name: digest((ROOT / name).read_bytes()) for name in inputs}
    assert after == input_hashes, 'Inputs changed during the test; rerun against final sources'
    report = dict(
        scope='Local P13270 complete-driver and exact minimum_rotation byte API checks; no online submission or AC.',
        mode=mode, status='pass', driver=DRIVER,
        problem_url='https://www.luogu.com.cn/problem/P13270',
        official_bounds='1 <= n <= 10000000; lowercase ASCII letters only',
        program_sha256=digest(program.encode()), core_sha256=digest(core_block.encode()),
        core_test_program_sha256=digest(core_program.encode()),
        pasted_program_sha256=digest(pasted_program.encode()), input_sha256=input_hashes,
        corpus_sha256=corpus.hexdigest(),
        compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0],
        platform=platform.platform(), flags=flags, compile_commands=commands,
        runtime_environment={key: env.get(key) for key in ['ASAN_OPTIONS', 'UBSAN_OPTIONS']},
        cases=counts, core_char_modes=['signed', 'unsigned'],
        core_case_runs=2 * len(byte_cases),
        notes=['Independent oracle enumerates every rotation for all small cases.',
               'Each maximum-size driver case uses an explicit structural expected string.',
               'Every driver answer is compared byte-for-byte including the final newline.',
               'The exact main also compiles/runs with only the named core and standard headers.',
               'Empty and arbitrary byte strings are core-interface extensions, not legal P13270 inputs.',
               'No vector<int> or negative-integer API is exposed or claimed.',
               'LeakSanitizer may be disabled by ASAN_OPTIONS; ASan/UBSan results are recorded separately.'])
    report_path = ROOT / f'verification/minimum-rotation-usage-{mode}.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
