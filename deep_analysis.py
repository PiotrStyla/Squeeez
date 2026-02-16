#!/usr/bin/env python3
"""
Deep Analysis of enwik9 structure for Decompose & Conquer compression.
Counts exact byte sizes of: XML metadata, internal links, templates,
categories, URLs, numeric data, timestamps, revision blocks.
"""
import re
import sys
from collections import Counter

def analyze_enwik9(path):
    print(f"Loading {path}...")
    with open(path, 'r', errors='ignore') as f:
        data = f.read()
    total_bytes = len(data)
    print(f"Total size: {total_bytes:,} bytes ({total_bytes/1024/1024:.1f} MB)\n")

    results = {}

    # 1. XML METADATA: <revision>...</revision> blocks (minus <text>)
    print("=" * 60)
    print("1. XML METADATA ANALYSIS")
    print("=" * 60)

    # Timestamps
    ts_pattern = re.compile(r'<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z</timestamp>')
    ts_matches = ts_pattern.findall(data)
    ts_bytes = sum(len(m) for m in ts_matches)
    print(f"  Timestamps: {len(ts_matches):,} occurrences, {ts_bytes:,} bytes ({ts_bytes/1024/1024:.2f} MB)")
    results['timestamps'] = ts_bytes

    # Revision IDs
    revid_pattern = re.compile(r'<id>\d+</id>')
    revid_matches = revid_pattern.findall(data)
    revid_bytes = sum(len(m) for m in revid_matches)
    print(f"  <id>...</id> tags: {len(revid_matches):,} occurrences, {revid_bytes:,} bytes ({revid_bytes/1024/1024:.2f} MB)")
    results['revision_ids'] = revid_bytes

    # Contributor blocks
    contrib_pattern = re.compile(r'<contributor>.*?</contributor>', re.DOTALL)
    contrib_matches = contrib_pattern.findall(data)
    contrib_bytes = sum(len(m) for m in contrib_matches)
    print(f"  <contributor>...</contributor>: {len(contrib_matches):,} occurrences, {contrib_bytes:,} bytes ({contrib_bytes/1024/1024:.2f} MB)")
    results['contributors'] = contrib_bytes

    # Username tags
    user_pattern = re.compile(r'<username>.*?</username>')
    user_matches = user_pattern.findall(data)
    user_bytes = sum(len(m) for m in user_matches)
    unique_users = len(set(user_matches))
    print(f"  <username>: {len(user_matches):,} occurrences ({unique_users:,} unique), {user_bytes:,} bytes ({user_bytes/1024/1024:.2f} MB)")
    results['usernames'] = user_bytes

    # Comment tags
    comment_pattern = re.compile(r'<comment>.*?</comment>')
    comment_matches = comment_pattern.findall(data)
    comment_bytes = sum(len(m) for m in comment_matches)
    print(f"  <comment>: {len(comment_matches):,} occurrences, {comment_bytes:,} bytes ({comment_bytes/1024/1024:.2f} MB)")
    results['comments'] = comment_bytes

    # Minor tags
    minor_bytes = data.count('<minor />') * len('<minor />')
    print(f"  <minor />: {data.count('<minor />'):,} occurrences, {minor_bytes:,} bytes")
    results['minor'] = minor_bytes

    # XML structure tags (page, revision, text, title, ns, etc.)
    xml_tags = ['<page>', '</page>', '<revision>', '</revision>', '<title>', '</title>',
                '<ns>', '</ns>', '<text ', '</text>', '<restrictions>', '</restrictions>']
    xml_struct_bytes = 0
    for tag in xml_tags:
        count = data.count(tag)
        tag_bytes = count * len(tag)
        xml_struct_bytes += tag_bytes
        if count > 0:
            print(f"  {tag}: {count:,} x {len(tag)} = {tag_bytes:,} bytes")
    results['xml_structure'] = xml_struct_bytes

    total_xml = sum(results[k] for k in ['timestamps', 'revision_ids', 'contributors',
                                          'usernames', 'comments', 'minor', 'xml_structure'])
    print(f"\n  TOTAL XML METADATA: {total_xml:,} bytes ({total_xml/1024/1024:.2f} MB) = {total_xml/total_bytes*100:.1f}%")
    results['total_xml'] = total_xml

    # 2. INTERNAL LINKS [[...]]
    print("\n" + "=" * 60)
    print("2. INTERNAL LINKS ANALYSIS")
    print("=" * 60)

    link_pattern = re.compile(r'\[\[([^\]]+)\]\]')
    link_matches = link_pattern.findall(data)
    link_full_bytes = sum(len(m) + 4 for m in link_matches)  # +4 for [[ ]]
    
    # Extract just the target (before |)
    link_targets = []
    for m in link_matches:
        target = m.split('|')[0].strip()
        link_targets.append(target)
    
    target_counter = Counter(link_targets)
    top_links = target_counter.most_common(100)

    print(f"  Total links: {len(link_matches):,}")
    print(f"  Total bytes (incl [[ ]]): {link_full_bytes:,} bytes ({link_full_bytes/1024/1024:.2f} MB)")
    print(f"  Unique targets: {len(target_counter):,}")
    print(f"\n  Top 30 most linked articles:")
    for i, (target, count) in enumerate(top_links[:30], 1):
        savings = count * (len(target) - 4)  # replace with 4-byte code
        print(f"    {i:3}. [{count:>6}x] '{target[:50]}' (save ~{savings:,} bytes)")

    # Calculate dictionary savings for top N
    for n in [1000, 5000, 10000]:
        top_n = target_counter.most_common(n)
        savings = sum(count * max(0, len(target) - 4) for target, count in top_n)
        coverage = sum(count for _, count in top_n)
        print(f"\n  Dictionary top {n:,}: covers {coverage:,}/{len(link_matches):,} links ({coverage/len(link_matches)*100:.1f}%), saves {savings:,} bytes ({savings/1024/1024:.2f} MB)")

    results['links_bytes'] = link_full_bytes
    results['links_count'] = len(link_matches)

    # 3. TEMPLATES {{...}}
    print("\n" + "=" * 60)
    print("3. TEMPLATES ANALYSIS")
    print("=" * 60)

    # Simple non-nested templates
    tmpl_pattern = re.compile(r'\{\{([^{}]+)\}\}')
    tmpl_matches = tmpl_pattern.findall(data)
    tmpl_bytes = sum(len(m) + 4 for m in tmpl_matches)

    tmpl_names = []
    for m in tmpl_matches:
        name = m.split('|')[0].strip()
        tmpl_names.append(name)

    tmpl_counter = Counter(tmpl_names)
    print(f"  Total templates: {len(tmpl_matches):,}")
    print(f"  Total bytes (incl {{ }}): {tmpl_bytes:,} bytes ({tmpl_bytes/1024/1024:.2f} MB)")
    print(f"  Unique template names: {len(tmpl_counter):,}")
    print(f"\n  Top 20 templates:")
    for i, (name, count) in enumerate(tmpl_counter.most_common(20), 1):
        print(f"    {i:3}. [{count:>6}x] '{name[:60]}'")
    results['templates_bytes'] = tmpl_bytes

    # 4. CATEGORIES [[Category:...]]
    print("\n" + "=" * 60)
    print("4. CATEGORIES ANALYSIS")
    print("=" * 60)

    cat_pattern = re.compile(r'\[\[Category:([^\]]+)\]\]')
    cat_matches = cat_pattern.findall(data)
    cat_bytes = sum(len(m) + 14 for m in cat_matches)  # +14 for [[Category: ]]
    cat_counter = Counter(cat_matches)
    print(f"  Total categories: {len(cat_matches):,}")
    print(f"  Total bytes: {cat_bytes:,} bytes ({cat_bytes/1024/1024:.2f} MB)")
    print(f"  Unique categories: {len(cat_counter):,}")
    print(f"  Top 20:")
    for i, (cat, count) in enumerate(cat_counter.most_common(20), 1):
        print(f"    {i:3}. [{count:>5}x] '{cat[:60]}'")
    results['categories_bytes'] = cat_bytes

    # 5. EXTERNAL URLs
    print("\n" + "=" * 60)
    print("5. EXTERNAL URLs ANALYSIS")
    print("=" * 60)

    url_pattern = re.compile(r'https?://[^\s\]<>\"]+')
    url_matches = url_pattern.findall(data)
    url_bytes = sum(len(u) for u in url_matches)
    print(f"  Total URLs: {len(url_matches):,}")
    print(f"  Total bytes: {url_bytes:,} bytes ({url_bytes/1024/1024:.2f} MB)")

    url_domains = []
    for u in url_matches:
        parts = u.split('/')
        if len(parts) >= 3:
            url_domains.append(parts[2])
    domain_counter = Counter(url_domains)
    print(f"  Unique domains: {len(domain_counter):,}")
    print(f"  Top 20 domains:")
    for i, (domain, count) in enumerate(domain_counter.most_common(20), 1):
        print(f"    {i:3}. [{count:>5}x] {domain}")
    results['urls_bytes'] = url_bytes

    # 6. NUMERIC DATA
    print("\n" + "=" * 60)
    print("6. NUMERIC DATA ANALYSIS")
    print("=" * 60)

    # Standalone numbers (at least 3 digits)
    num_pattern = re.compile(r'\b\d[\d,]{2,}\b')
    num_matches = num_pattern.findall(data[:200000000])  # First 200MB for speed
    num_bytes_sample = sum(len(n) for n in num_matches)
    num_bytes_est = int(num_bytes_sample * total_bytes / 200000000)
    print(f"  Numbers (3+ digits, sample 200MB): {len(num_matches):,}")
    print(f"  Bytes in sample: {num_bytes_sample:,}")
    print(f"  Estimated total: {num_bytes_est:,} bytes ({num_bytes_est/1024/1024:.2f} MB)")
    results['numbers_bytes'] = num_bytes_est

    # 7. xml:space="preserve" and other repeated XML attributes
    print("\n" + "=" * 60)
    print("7. REPEATED PATTERNS")
    print("=" * 60)

    patterns_to_check = [
        ('xml:space="preserve"', 'xml:space attr'),
        ('align="center"', 'align center'),
        ('align="right"', 'align right'),
        ('align="left"', 'align left'),
        ('colspan=', 'colspan'),
        ('rowspan=', 'rowspan'),
        ('style="', 'style attr'),
        ('#REDIRECT', 'redirects'),
        ('&amp;', 'HTML &amp;'),
        ('&lt;', 'HTML &lt;'),
        ('&gt;', 'HTML &gt;'),
        ('&quot;', 'HTML &quot;'),
    ]

    repeated_total = 0
    for pattern, name in patterns_to_check:
        count = data.count(pattern)
        pbytes = count * len(pattern)
        repeated_total += pbytes
        if count > 0:
            print(f"  {name}: {count:,} x {len(pattern)} = {pbytes:,} bytes ({pbytes/1024/1024:.2f} MB)")
    results['repeated_patterns'] = repeated_total

    # 8. SUMMARY
    print("\n" + "=" * 60)
    print("GRAND SUMMARY — Decompose & Conquer Potential")
    print("=" * 60)

    categories = [
        ('XML Metadata', results['total_xml']),
        ('Internal Links', results['links_bytes']),
        ('Templates', results['templates_bytes']),
        ('Categories', results['categories_bytes']),
        ('External URLs', results['urls_bytes']),
        ('Numeric Data (est)', results['numbers_bytes']),
        ('Repeated Patterns', results['repeated_patterns']),
    ]

    grand_total = 0
    for name, size in categories:
        pct = size / total_bytes * 100
        print(f"  {name:25} {size:>12,} bytes ({size/1024/1024:>7.2f} MB) = {pct:5.1f}%")
        grand_total += size

    remaining = total_bytes - grand_total
    print(f"  {'Pure article text (est)':25} {remaining:>12,} bytes ({remaining/1024/1024:>7.2f} MB) = {remaining/total_bytes*100:5.1f}%")
    print(f"  {'─' * 60}")
    print(f"  {'TOTAL IDENTIFIED':25} {grand_total:>12,} bytes ({grand_total/1024/1024:>7.2f} MB) = {grand_total/total_bytes*100:5.1f}%")

    print(f"\n  Current baseline (paq8px -5):  134,301,074 bytes (128.1 MB)")
    print(f"  World record (STARLIT+cmix):   114,700,000 bytes (109.4 MB)")
    print(f"\n  If stream separation gives 10-20% better compression on identified streams:")
    for pct in [10, 15, 20]:
        saved = int(grand_total * pct / 100)
        # But PAQ already compresses well, so the actual saving after PAQ is smaller
        paq_factor = 0.15  # PAQ compresses to ~15%
        real_saved = int(saved * paq_factor)
        print(f"    {pct}% improvement on {grand_total/1024/1024:.0f} MB → ~{real_saved:,} bytes ({real_saved/1024/1024:.2f} MB) after PAQ")

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '/root/hutter/paq8px/enwik9_reordered_transformed'
    analyze_enwik9(path)
