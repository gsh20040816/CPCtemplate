import subprocess
import sys

secret = int(sys.argv[1])
assert 1 <= secret <= 100
p = subprocess.Popen([sys.argv[2]], stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, text=True, bufsize=1)
try:
    queries = 0
    while True:
        line = p.stdout.readline()
        print('solution:', line.rstrip(), file=sys.stderr, flush=True)
        parts = line.split()
        assert len(parts) == 2, 'EOF or malformed output'
        kind, value = parts[0], int(parts[1])
        if kind == '!':
            assert value == secret, 'wrong answer'
            p.stdin.close()
            assert p.wait(timeout=1) == 0, 'nonzero exit'
            assert not p.stdout.read().strip(), 'extra output'
            break
        assert kind == '?' and 1 <= value <= 100
        queries += 1
        assert queries <= 7, 'too many queries'
        reply = int(secret <= value)
        print('judge:', reply, file=sys.stderr, flush=True)
        p.stdin.write(str(reply) + '\n')
        p.stdin.flush()
    print('AC', file=sys.stderr)
finally:
    if p.poll() is None:
        p.kill()
    p.wait()
