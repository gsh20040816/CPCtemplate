#!/usr/bin/env python3
"""Audit copied usage programs without expanding their local include files.

Checks syntax/copyability, not algorithm correctness, sanitizer behavior or online
AC. Sources and diagnostics are retained in a fresh output directory; the JSON
report embeds all candidates so it can be archived independently of that folder.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PRELUDE = '#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
FLAGS = ['-std=c++20', '-fsyntax-only']
SCOPE = 'Syntax/copyability only; no runtime correctness, sanitizer or online AC claim.'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def utc_now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def snapshot(paths):
    return {str(p.relative_to(ROOT)): digest(p.read_bytes())
            for p in sorted(set(paths))}


def extract_components(catalog):
    """Use the marker/struct-span extraction rules of tools/book.py exactly."""
    entries = []
    for module, symbol, title, info in catalog:
        path = ROOT / 'src/compact' / (module + '.hpp')
        lines = path.read_text().splitlines()
        marker = '// BEGIN ' + symbol
        if marker in lines:
            start = lines.index(marker) + 1
            end = lines.index('// END ' + symbol, start)
        else:
            starts = []
            for i, line in enumerate(lines):
                match = re.match(r'^(?:template.*?\s+)?struct\s+(\w+)', line)
                if match:
                    starts.append((i, match[1]))
            index = next(i for i, value in enumerate(starts) if value[1] == symbol)
            start = starts[index][0]
            end = starts[index + 1][0] if index + 1 < len(starts) else len(lines)
            if start and lines[start - 1].startswith('template'):
                start -= 1
            if end and lines[end - 1].startswith('template'):
                end -= 1
        code = '\n'.join(lines[start:end])
        entries.append(dict(module=module, symbol=symbol, title=title, code=code,
                            code_sha256=digest(code.encode()),
                            source=str(path.relative_to(ROOT)),
                            first_line=start + 1, last_line=end,
                            documented_gnu_headers=list(dict.fromkeys(
                                h.rstrip('.') for h in re.findall(r'\bext/[A-Za-z0-9_./]+', info)))))
    if len({e['symbol'] for e in entries}) != len(entries):
        raise ValueError('Duplicate catalog symbols')
    return entries


def topological_closure(names, dependencies):
    result, seen, visiting = [], set(), set()

    def visit(name):
        if name in seen:
            return
        if name in visiting:
            raise ValueError('Documented dependency cycle at ' + name)
        visiting.add(name)
        for dependency in dependencies[name]:
            visit(dependency)
        visiting.remove(name)
        seen.add(name)
        result.append(name)

    for name in names:
        visit(name)
    return result


def compare_cache(entries, dependencies):
    path = ROOT / 'build/book-sections.json'
    if not path.exists():
        return {'present': False}
    raw = path.read_bytes()
    cached = {e['symbol']: e for e in json.loads(raw)}
    current = {e['symbol']: e for e in entries}
    return {'present': True, 'sha256': digest(raw),
            'missing_symbols': sorted(current.keys() - cached.keys()),
            'extra_symbols': sorted(cached.keys() - current.keys()),
            'code_mismatches': [s for s in current.keys() & cached.keys()
                                if current[s]['code'] != cached[s]['code']],
            'dependency_mismatches': [s for s in current.keys() & cached.keys()
                                      if dependencies[s] != cached[s].get('dependencies')],
            'note': 'Informational cache cross-check only; candidates use current header regions.'}


def candidate(row, names, components, headers=()):
    program = ''.join('#include <' + h + '>\n' for h in headers)
    # cassert follows ext/rope, matching the documented assertion workaround.
    program += PRELUDE + '\n\n'.join(components[n]['code'] for n in names)
    program += '\n\n' + row['snippet']
    return dict(id=row['id'], symbol=row['symbol'], driver=row['driver'],
                original_requires=row['requires'], copied_components=names,
                added_documented_gnu_headers=list(headers),
                snippet_sha256=digest(row['snippet'].encode()),
                program_sha256=digest(program.encode()), program=program)


def compile_stage(name, candidates, output, compiler, jobs, timeout):
    folder = output / name
    folder.mkdir()

    def compile_one(item):
        source = folder / (item['id'] + '.cpp')
        log = folder / (item['id'] + '.log')
        source.write_text(item['program'])
        command = [compiler, *FLAGS, str(source)]
        started = time.monotonic()
        try:
            proc = subprocess.run(command, capture_output=True, text=True,
                                  timeout=timeout)
            code, diagnostics = proc.returncode, proc.stdout + proc.stderr
            timed_out = False
        except subprocess.TimeoutExpired as error:
            def as_text(value):
                return value.decode(errors='replace') if isinstance(value, bytes) else value or ''
            diagnostics = as_text(error.stdout) + as_text(error.stderr) + '\nCompiler timeout\n'
            code, timed_out = None, True
        log.write_text(diagnostics)
        return {**item, 'returncode': code, 'timed_out': timed_out,
                'seconds': round(time.monotonic() - started, 3),
                'source_file': str(source.relative_to(output)),
                'diagnostics_file': str(log.relative_to(output)),
                'diagnostics': diagnostics,
                'diagnostics_sha256': digest(diagnostics.encode()),
                'source_sha256_after': digest(source.read_bytes())}

    results = []
    print(name + ': ' + str(len(candidates)) + ' candidates', flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        pending = [pool.submit(compile_one, item) for item in candidates]
        for future in concurrent.futures.as_completed(pending):
            result = future.result()
            results.append(result)
            if result['returncode'] != 0:
                first = next((line for line in result['diagnostics'].splitlines()
                              if 'error:' in line), 'See compiler diagnostics')
                print('  FAIL ' + result['id'] + ' (' + result['symbol'] + '): ' + first,
                      flush=True)
            if len(results) % 25 == 0:
                print('  completed ' + str(len(results)), flush=True)
    order = {item['id']: i for i, item in enumerate(candidates)}
    results.sort(key=lambda item: order[item['id']])
    stage = {'name': name, 'count': len(results),
             'passed': sum(r['returncode'] == 0 for r in results),
             'failed': sum(r['returncode'] != 0 for r in results), 'results': results}
    save_json(folder / 'report.json', stage)
    print(name + ': ' + str(stage['passed']) + ' pass, ' + str(stage['failed']) + ' fail', flush=True)
    return stage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build/copy-context-audit',
                        help='Fresh output directory; an existing path is never overwritten')
    parser.add_argument('--compiler', default='g++', help='C++ compiler executable (default: g++)')
    parser.add_argument('--jobs', type=int, choices=range(1, 5), default=4,
                        help='Concurrent syntax-only compiles, from 1 to 4 (default: 4)')
    parser.add_argument('--timeout', type=float, default=120,
                        help='Maximum seconds per compiler invocation (default: 120)')
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    compiler = shutil.which(args.compiler)
    if compiler is None:
        parser.error('Compiler not found: ' + args.compiler)
    compiler = str(Path(compiler).resolve())
    output = args.output_dir.resolve()
    if not output.is_relative_to(ROOT / 'build'):
        parser.error('--output-dir must be beneath this repository\'s build directory')
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.error('Output path already exists; choose a fresh --output-dir')
    report = {'schema_version': 1, 'scope': SCOPE, 'started_utc': utc_now(),
              'compiler': {'path': compiler, 'sha256': digest(Path(compiler).read_bytes()),
                           'version': subprocess.check_output([compiler, '--version'], text=True)},
              'flags': FLAGS, 'jobs': args.jobs, 'timeout_seconds': args.timeout,
              'prelude': PRELUDE, 'stages': []}
    try:
        from usage_examples import records
        from template_dependencies import dependencies
        raw_rows = json.loads((ROOT / 'docs/usage-examples.json').read_text())
        paths = [ROOT / name for name in ['tools/audit_copy_context.py', 'tools/book.py',
                 'tools/usage_examples.py', 'tools/template_dependencies.py',
                 'docs/catalog.json', 'docs/usage-examples.json', 'docs/template-dependencies.json']]
        paths += [p for p in (ROOT / 'src').rglob('*') if p.is_file()]
        paths += [ROOT / row['driver'] for row in raw_rows]
        report['input_sha256_before'] = snapshot(paths)
        report['tool_sha256'] = report['input_sha256_before']['tools/audit_copy_context.py']
        catalog = json.loads((ROOT / 'docs/catalog.json').read_text())
        entries = extract_components(catalog)
        computed = dependencies(entries)
        documented = json.loads((ROOT / 'docs/template-dependencies.json').read_text())
        report['computed_dependencies'] = computed
        report['documented_dependencies'] = documented
        if computed != documented:
            raise ValueError('Current core dependency extraction differs from documented template-dependencies.json')
        report['book_cache_cross_check'] = compare_cache(entries, documented)
        report['components'] = entries
        rows = records()  # Read-only snippet extraction; expanded row.program is never used.
        if len({row['id'] for row in rows}) != len(rows):
            raise ValueError('Duplicate usage IDs')
        for row in rows:
            if not re.fullmatch(r'[A-Za-z0-9_-]+', row['id']):
                raise ValueError('Unsafe usage ID: ' + row['id'])
        report['registered_count'] = len(rows)
        report['component_count'] = len(entries)
        components = {e['symbol']: e for e in entries}
        closure = {r['id']: topological_closure(r['requires'], documented) for r in rows}
        direct = [candidate(r, r['requires'], components) for r in rows]
        closed = [candidate(r, closure[r['id']], components) for r in rows]
        for name, programs in [('01-direct-declared-order', direct),
                               ('02-documented-topological-closure', closed)]:
            report['stages'].append(compile_stage(name, programs, output, compiler,
                                                  args.jobs, args.timeout))
            save_json(output / 'report.json', report)
        failed = {r['id'] for r in report['stages'][1]['results'] if r['returncode'] != 0}
        supplements = []
        for row in rows:
            if row['id'] not in failed:
                continue
            names = closure[row['id']]
            headers = list(dict.fromkeys(h for n in names
                                        for h in components[n]['documented_gnu_headers']))
            if headers:
                supplements.append(candidate(row, names, components, headers))
        report['stages'].append(compile_stage('03-explicit-catalog-gnu-headers', supplements,
                                              output, compiler, args.jobs, args.timeout))
        resolved = {r['id'] for r in report['stages'][2]['results'] if r['returncode'] == 0}
        report['unresolved_ids'] = sorted(failed - resolved)
        report['unresolved_count'] = len(report['unresolved_ids'])
        report['input_sha256_after'] = snapshot(paths)
        report['changed_inputs'] = [p for p, value in report['input_sha256_before'].items()
                                   if report['input_sha256_after'][p] != value]
        report['compiler_unchanged'] = digest(Path(compiler).read_bytes()) == report['compiler']['sha256']
        report['candidate_hashes_verified'] = all(
            digest((output / r['source_file']).read_bytes()) == r['program_sha256']
            for stage in report['stages'] for r in stage['results'])
        report['infrastructure_errors'] = [r['id'] for stage in report['stages']
                                          for r in stage['results']
                                          if r['timed_out'] or r['returncode'] not in (0, 1)]
        report['finished_utc'] = utc_now()
        invalid = (report['changed_inputs'] or not report['compiler_unchanged'] or
                   not report['candidate_hashes_verified'] or report['infrastructure_errors'])
        report['exit_status'] = 2 if invalid else int(bool(report['unresolved_count']))
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
        report['finished_utc'] = utc_now()
        report['exit_status'] = 2
    save_json(output / 'report.json', report)
    print('Report: ' + str(output / 'report.json'))
    if 'error' in report:
        print('Audit error: ' + report['error'], file=sys.stderr)
    else:
        print('Unresolved after documented prerequisites: ' + str(report['unresolved_count']))
        print('Input hashes unchanged: ' + str(not report['changed_inputs']))
    print(SCOPE)
    return report['exit_status']


if __name__ == '__main__':
    raise SystemExit(main())
