"""Named copy dependencies from catalog code, independent of header over-inclusion."""
import re


def code_tokens(code):
    # Preserve string tokens as a unit before dropping them, so // inside a string
    # cannot turn the remaining source into a fictitious comment.
    pattern = r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\b[A-Za-z_]\w*\b'
    return {s for s in re.findall(pattern, code, re.S)
            if not s.startswith(('//', '/*', '"', "'"))}


def dependencies(entries):
    names = {r['symbol'] for r in entries}
    result = {}
    for row in entries:
        result[row['symbol']] = sorted((code_tokens(row['code']) & names) - {row['symbol']})
    # Generic parameters are not concrete library dependencies. The caller must
    # supply their operations; specific uses are linked by each usage record.
    return result


def reference(symbol):
    label = 'compact-' + symbol
    title = symbol.replace('_', r'\_')
    return r'\hyperref[' + label + ']{' + title + r'}（第~\pageref{' + label + r'}~页，\ref{' + label + r'}~节）'


def references(symbols):
    return '、'.join(reference(s) for s in symbols)
