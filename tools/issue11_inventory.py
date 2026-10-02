#!/usr/bin/env python3
"""Record attachment headings and derive accounting, never new coverage claims."""
import argparse
from collections import Counter
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_VERIFIED = frozenset({
    'existing_implementation_local_verified',
    'existing_formula_implementation_local_verified',
    'implemented_local_verified_online_pending',
    'implemented_application_local_verified_online_pending',
})
PARTIAL = 'reviewed_partial_coverage'
PENDING = 'pending_content_review'
STATUSES = LOCAL_VERIFIED | {PARTIAL, PENDING}


def hierarchy_summary(entries):
    """Count terminal headings once; original parent status is not a leaf vote.

    A local-verification status is restricted to its original review contract.
    No existing enum proves full attachment coverage or online acceptance.
    """
    by_section = {row['section']: row for row in entries}
    assert len(by_section) == len(entries), 'duplicate section'
    children = {section: [] for section in by_section}
    for row in entries:
        section = row['section']
        assert re.fullmatch(r'[1-9]\d*(?:\.[1-9]\d*)*', section), section
        assert row['level'] == section.count('.'), (section, 'incorrect level')
        assert row['status'] in STATUSES, (section, 'unknown status')
        if '.' in section:
            parent = section.rsplit('.', 1)[0]
            assert parent in children, (section, 'missing parent')
            children[parent].append(section)

    leaves = [row for row in entries if not children[row['section']]]

    def counts(rows):
        statuses = Counter(row['status'] for row in rows)
        return dict(
            leaf_count=len(rows),
            leaf_status_counts=dict(sorted(statuses.items())),
            reviewed_leaf_count=len(rows) - statuses[PENDING],
            locally_verified_leaf_count=sum(statuses[s] for s in LOCAL_VERIFIED),
            partial_leaf_sections=[row['section'] for row in rows if row['status'] == PARTIAL],
            pending_content_leaf_sections=[row['section'] for row in rows if row['status'] == PENDING],
            explicit_online_pending_leaf_count=sum(
                count for status, count in statuses.items() if status.endswith('_online_pending')),
            all_leaves_content_reviewed=bool(rows) and statuses[PENDING] == 0,
            all_leaves_locally_verified=bool(rows) and all(row['status'] in LOCAL_VERIFIED for row in rows),
        )

    parents = []
    for row in entries:
        section = row['section']
        if not children[section]:
            continue
        descendants = [child for child in entries if child['section'].startswith(section + '.')]
        if row['status'] in LOCAL_VERIFIED:
            assert all(child['status'] in LOCAL_VERIFIED for child in descendants), (
                section, 'locally verified parent has a partial/pending descendant')
        selected = [leaf for leaf in leaves if leaf['section'].startswith(section + '.')]
        parents.append(dict(section=section, direct_child_sections=children[section], **counts(selected)))
    return dict(
        schema_version=1,
        counting_unit='terminal section headings; parent headings are not additional implementations',
        scope_note='Counts retain each original review contract. Reviewed/local evidence does not prove '
                   'all variants, application adaptations, formal-template coverage, online AC or ranking.',
        heading_count=len(entries),
        chapter_heading_count=sum(row['level'] == 0 for row in entries),
        main_topic_heading_count=sum(row['level'] == 1 for row in entries),
        variant_heading_count=sum(row['level'] > 1 for row in entries),
        parent_heading_count=len(parents),
        recorded_pending_parent_sections=[row['section'] for row in entries
                                          if children[row['section']] and row['status'] == PENDING],
        attachment_complete=False,
        **counts(leaves),
        parents=parents,
    )


def render_inventory(data):
    """Render both the unchanged source-row register and its derived summary."""
    rows = data['entries']
    summary = data['hierarchy_summary']
    by_section = {row['section']: row for row in rows}
    lines = ['# Issue 11 附件核对清单', '',
             f"附件共 {data['pdf_pages']} 页、{summary['main_topic_heading_count']} 个主要主题，"
             f"连同章节和变体共 {len(rows)} 个目录项。PDF SHA-256：`{data['pdf_sha256']}`。", '',
             '目录页码与实际 PDF 页码分别保留；正文标题已用于定位起始页。标题相同只产生候选，不等于实现或验证完成。', '',
             '## 层级统计与原登记状态', '',
             f"{len(rows)} 行由 {summary['chapter_heading_count']} 个章节、"
             f"{summary['main_topic_heading_count']} 个主要主题和 {summary['variant_heading_count']} 个变体组成。"
             f"其中 {summary['parent_heading_count']} 行有子项，{summary['leaf_count']} 行是最末级条目（叶项）；"
             '主题有变体时只数最末级变体，不能把父项与子项相加当作独立实现数。', '',
             f"当前 {summary['reviewed_leaf_count']} 个叶项已有正文核对记录，"
             f"{summary['locally_verified_leaf_count']} 个叶项的原状态登记了契约内的本地验证；"
             f"{len(summary['partial_leaf_sections'])} 个叶项仍为部分覆盖，"
             f"{len(summary['pending_content_leaf_sections'])} 个叶项待正文核对。"
             '本地验证数量不是全功能完成数量，更不是线上 AC 数量。', '',
             f"原状态中有 {summary['explicit_online_pending_leaf_count']} 个叶项显式带 `online_pending`；"
             '其余叶项没有这个后缀也不构成线上通过证据。所有原 `status`、`review` 和来源行保持不变。', '',
             '| 章节 | 原父项状态 | 主要主题数 | 叶项数 | 已核对叶项 | 契约内本地验证叶项 | 部分覆盖叶项 | 待正文核对叶项 | 显式线上待验证叶项 |',
             '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for parent in summary['parents']:
        section = parent['section']
        if by_section[section]['level'] != 0:
            continue
        row = by_section[section]
        lines.append(f"| {section} {row['title']} | {row['status']} | {len(parent['direct_child_sections'])} | "
                     f"{parent['leaf_count']} | {parent['reviewed_leaf_count']} | "
                     f"{parent['locally_verified_leaf_count']} | {len(parent['partial_leaf_sections'])} | "
                     f"{len(parent['pending_content_leaf_sections'])} | {parent['explicit_online_pending_leaf_count']} |")
    pending_parents = '、'.join(summary['recorded_pending_parent_sections']) or '无'
    partial_leaves = '、'.join(summary['partial_leaf_sections']) or '无'
    lines += ['', f'父项原登记待正文核对：{pending_parents}。其子项汇总与原父项状态分开读取；'
              '若子项均已有审阅记录，不能再把父项的旧登记解释为整章尚未审阅，也不能反过来抹掉线上或契约范围缺口。',
              f'最末级部分覆盖项：{partial_leaves}。全部父项（含主题下变体）的计算结果见 JSON 的 `hierarchy_summary.parents`。', '',
              '## 全部原始目录项', '',
              '| 节号 | 标题 | 原目录页 | PDF 实际页 | 状态 |', '|---|---|---:|---:|---|']
    for row in rows:
        lines.append(f"| {row['section']} | {row['title']} | {row['toc_page']} | "
                     f"{row['physical_page']} | {row['status']} |")
    lines += ['', '## 仍须保留的范围限制', '',
              '- 6.5.2 浮点极角排序仍缺稳健谓词、数值契约及验证；整数比较器不替代这个变体。'
              '因此 6.5 和第 6 章不能记为全覆盖。见 [几何核对](GEOMETRY-ATTACHMENT.md)。',
              '- 6.1 的定点凸包只覆盖约定小数位输入；6.4 的整数有界半平面交不提供通用浮点半平面交、无界分类。'
              '这类接口范围限制不会仅因叶项登记本地验证而消失。见 [几何核对](GEOMETRY-ATTACHMENT.md)。',
              '- 4.2.2 爱莲说、4.3.1 牛客变体仍保留原题外部身份/线上验证限制；6.5.1 没有明确 Seoul 原题或完整应用。'
              '竞赛应用及本地接口用法不代替正式模板题覆盖，普通 LCT 的证据不替代虚子树变体。'
              '见 [路径乘积](TREE-PATH-PRODUCTS.md)、[位翻转](SEQUENCE-FLIP.md)及 [几何核对](GEOMETRY-ATTACHMENT.md)。',
              '- 3.4 LGV 只证明所列 DAG 接口，3.7 Matrix-Tree 不含引用题 P4336/P3317 的完整应用适配；'
              '3.1 Min25 不承诺任意次数或全部时限，5.1 一般插值公式不等于快速插值实现。'
              '详见各项原 `review` 及所链接的专项核对，不能由章节汇总扩大能力范围。',
              '- 旧 [多项式基础核对](POLYNOMIAL-ATTACHMENT-BASE.md) 的 5.2 待补段和 '
              '[递推核对](RECURRENCE-ATTACHMENT.md) 的 5.12 待补段是较早批次记录；'
              '这两项当前登记依据是后续 [浮点 FFT 核对](FFT-ATTACHMENT.md) 与各自原 `review`。'
              '保留后续记录的舍入、平台、长度和系数限制，不恢复已补的旧缺口，也不新增实现/验证结论。', '',
              '来源为 issue #11 用户提供附件；完整 PDF 留在本地 build 中，仓库仅登记来源、摘要与覆盖状态。',
              '已核对项与实现、验证范围见 JSON 中各项 review；本地通过不等于线上 AC，其余目录按上表状态继续核对，不排除任何主题或变体。', '',
              '## 复算与一致性检查', '',
              '`python3 tools/issue11_inventory.py --refresh-summary` 仅从现有登记复算 JSON 汇总并重写本页，不读取或生成 PDF。',
              '`python3 tests/issue11_rollup.py` 校验固定来源、层级计数、父子状态约束和本页一致性，含伪造完成状态的负对照；不运行算法或新增 OJ 结论。',
              '原 `python3 tools/issue11_inventory.py <原附件.pdf>` 入口仍可重建定位，但要求同一 SHA-256 和完全相同的来源行，保留原状态与 review，并重新计算汇总。']
    return '\n'.join(lines) + '\n'


def inventory_from_pdf(pdf, prior):
    sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if prior:
        assert sha == prior['pdf_sha256'], 'Attachment changed; review before replacing scope'
    text = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
    pages = text.split('\f')
    if not pages[-1].strip():
        pages.pop()
    old = {row['section']: row for row in prior.get('entries', [])}
    norm = lambda value: re.sub(r'\s+', '', value)
    rows = []
    for page in pages[:3]:
        for line in page.splitlines():
            match = re.match(r'^\s*(\d+(?:\.\d+)*)\s+(.+?)\s+(\d+)\s*$', line)
            if not match:
                continue
            section, title, number = match.groups()
            title = re.sub(r'(?:\s*\.\s*){2,}$', '', title).strip()
            target = norm(section + title)
            hits = [i for i, body in enumerate(pages[3:], 4)
                    if any(norm(value).startswith(target) for value in body.splitlines())]
            assert hits, (section, title)
            row = dict(section=section, title=title, toc_page=int(number),
                       physical_page=hits[0], level=section.count('.'),
                       status=PENDING, candidate_symbols=[])
            for key in ['status', 'candidate_symbols', 'review']:
                if key in old.get(section, {}):
                    row[key] = old[section][key]
            rows.append(row)
    assert len(rows) == 88 and sum(row['level'] == 1 for row in rows) == 55
    assert len({row['section'] for row in rows}) == len(rows)
    data = dict(issue='https://github.com/gsh20040816/CPCtemplate/issues/11',
                url='https://github.com/user-attachments/files/32176902/default.pdf',
                pdf_sha256=sha, pdf_bytes=pdf.stat().st_size, pdf_pages=len(pages),
                scope_note='All 88 chapter/topic/variant headings retained, including 55 main topics. Physical start pages matched against body headings, not copied from stale TOC numbers. No coverage is inferred from titles.',
                entries=rows)
    if prior:
        for key in ('issue', 'url', 'pdf_sha256', 'pdf_bytes', 'pdf_pages', 'scope_note'):
            assert data[key] == prior[key], ('source provenance changed', key)
        source_keys = ('section', 'title', 'toc_page', 'physical_page', 'level')
        assert [[row[key] for key in source_keys] for row in rows] == [
            [row[key] for key in source_keys] for row in prior['entries']], 'source rows changed'
        # Keep original records (including future review metadata), not just known fields.
        data = dict(prior)
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path, nargs='?')
    parser.add_argument('--refresh-summary', action='store_true',
                        help='recompute only from the existing inventory, without reading a PDF')
    args = parser.parse_args(argv)
    if bool(args.pdf) == args.refresh_summary:
        parser.error('provide either the original PDF or --refresh-summary')
    path = ROOT / 'docs/issue11-inventory.json'
    prior = json.loads(path.read_text()) if path.exists() else {}
    if args.refresh_summary:
        assert prior, 'an existing source inventory is required'
        data = dict(prior)
    else:
        data = inventory_from_pdf(args.pdf, prior)
    data['hierarchy_summary'] = hierarchy_summary(data['entries'])
    markdown = render_inventory(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'docs/ISSUE-11.md').write_text(markdown)
    summary = data['hierarchy_summary']
    print(f"Issue 11: {summary['heading_count']} headings, {summary['parent_heading_count']} parents, "
          f"{summary['leaf_count']} leaves; {summary['locally_verified_leaf_count']} locally verified, "
          f"{len(summary['partial_leaf_sections'])} partial, "
          f"{len(summary['pending_content_leaf_sections'])} content pending; attachment not complete")


if __name__ == '__main__':
    main()
