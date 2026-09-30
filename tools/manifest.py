#!/usr/bin/env python3
"""Aggregate two explicitly selected, current source-bound full-suite receipts."""
import argparse
import datetime
import json
from pathlib import Path
from run_provenance import baseline_archive, baseline_hashes, snapshot, validate_receipt


def build_manifest(root, normal, sanitizer):
    source = snapshot(root)
    baseline = baseline_hashes(baseline_archive(root))
    runs = {mode: validate_receipt(root, path, mode, source, baseline)
            for mode, path in [('normal', normal), ('sanitizer', sanitizer)]}
    if runs['normal']['start']['run_id'] == runs['sanitizer']['start']['run_id']:
        raise ValueError('normal and sanitizer must be distinct runs')
    if snapshot(root) != source:
        raise ValueError('inputs changed while validating receipts')
    return {'schema': 'cpc-verification-manifest-v1',
            'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'verification': 'Local full-suite oracles and ASan/UBSan, not OJ acceptance or a universal correctness proof; no LeakSanitizer certification',
            'source_sha256': source, 'runs': runs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--normal', type=Path, required=True, help='normal receipt.json')
    parser.add_argument('--sanitizer', type=Path, required=True, help='sanitizer receipt.json')
    parser.add_argument('--output', type=Path, required=True, help='new file under verification/runs (never overwritten)')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        output = args.output.resolve()
        if not output.is_relative_to((root / 'verification/runs').resolve()):
            raise ValueError('output must be under verification/runs; historical evidence is preserved')
        manifest = build_manifest(root, args.normal, args.sanitizer)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x') as stream:
            json.dump(manifest, stream, indent=2)
            stream.write('\n')
        print(output)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Manifest rejected: {error}\n')


if __name__ == '__main__':
    main()
