#!/usr/bin/env python3
"""
Combined Census + Link Dictionary + Metadata Compression for enwik9.
Applies all three transforms in one pass for maximum preprocessing gain.
"""
import re
import struct
import sys
import os
from collections import Counter

DICT_SIZE = 10000
LINK_MARKER = b'\x01'
META_MARKER = b'\x02'

def flush_print(msg):
    print(msg, flush=True)

# ─── US States ───
US_STATES = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
}
STATE_TO_ID = {v: i for i, v in enumerate(sorted(US_STATES.values()))}

CENSUS_PATTERNS = {
    'population': r'there were (\d[\d,]*) people',
    'households': r'(\d[\d,]*) households',
    'families': r'(\d[\d,]*) families',
    'density_pop': r'population density (?:was |of )?(\d[\d,\.]*)',
    'median_income_household': r'median income for a household[^$]*\$(\d[\d,]*)',
    'median_income_family': r'median income for a family[^$]*\$(\d[\d,]*)',
    'per_capita': r'per capita income[^$]*\$(\d[\d,]*)',
    'males': r'(\d[\d,]*) males',
    'females': r'(\d[\d,]*) females',
    'land_area': r'land area of (\d[\d,\.]*)',
    'water_area': r'water area of (\d[\d,\.]*)',
    'zip_code': r'ZIP code[^\d]*(\d{5})',
    'area_code': r'area code[^\d]*(\d{3})',
}

FIELD_IDS = {
    'population': 1, 'households': 2, 'families': 3,
    'median_income_household': 4, 'median_income_family': 5, 'per_capita': 6,
    'males': 7, 'females': 8, 'zip_code': 9, 'area_code': 10,
}

def parse_number(s):
    if not s: return 0
    return int(s.replace(',', '').split('.')[0])

def detect_census(title, text):
    for state_name in US_STATES:
        if state_name in title or f', {US_STATES[state_name]}' in title:
            if 'census' in text.lower() and 'population' in text.lower():
                return True, state_name
    return False, None

def extract_census_data(text):
    data = {}
    for key, pattern in CENSUS_PATTERNS.items():
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                data[key] = parse_number(m.group(1))
            except:
                pass
    return data

def encode_census_binary(title, state, data):
    title_bytes = title.encode('utf-8')[:255]
    state_code = US_STATES.get(state, 'XX')
    state_id = STATE_TO_ID.get(state_code, 99)
    result = bytearray()
    result.append(0xCE)
    result.append(len(title_bytes))
    result.extend(title_bytes)
    result.append(state_id)
    fields = []
    for key, value in data.items():
        if key in FIELD_IDS and value:
            fields.append((FIELD_IDS[key], min(value, 0xFFFFFFFF)))
    result.append(len(fields))
    for fid, val in fields:
        result.append(fid)
        result.extend(struct.pack('<I', val))
    return bytes(result)

# ─── Phase 1: Census extraction (returns ranges to replace) ───
def phase_census(data):
    flush_print("PHASE 1: Census Template Extraction")
    article_pat = re.compile(r'<title>(.*?)</title>.*?<text[^>]*>(.*?)</text>', re.DOTALL)
    
    census_replacements = []  # (start, end, binary_data)
    count = 0
    bytes_saved = 0
    
    for m in article_pat.finditer(data):
        title = m.group(1)
        text = m.group(2)
        is_census, state = detect_census(title, text)
        if is_census:
            census_data = extract_census_data(text)
            if len(census_data) >= 3:
                binary = encode_census_binary(title, state, census_data)
                orig_len = m.end() - m.start()
                if len(binary) < orig_len:
                    census_replacements.append((m.start(), m.end(), binary))
                    bytes_saved += orig_len - len(binary)
                    count += 1
                    if count % 1000 == 0:
                        flush_print(f"  Census articles: {count}...")
    
    flush_print(f"  Census articles found: {count:,}")
    flush_print(f"  Census bytes saved: {bytes_saved:,} ({bytes_saved/1024/1024:.2f} MB)")
    return census_replacements

# ─── Phase 2: Link Dictionary (on remaining text) ───
def phase_links(data, census_ranges):
    flush_print("PHASE 2: Link Dictionary")
    
    # Build set of excluded ranges (census articles)
    census_set = set()
    for start, end, _ in census_ranges:
        census_set.add((start, end))
    
    link_pat = re.compile(r'\[\[([^\]]+)\]\]')
    target_counter = Counter()
    link_matches = []
    
    for m in link_pat.finditer(data):
        # Skip links inside census articles
        in_census = False
        for cs, ce, _ in census_ranges:
            if cs <= m.start() < ce:
                in_census = True
                break
        if in_census:
            continue
        
        full = m.group(1)
        target = full.split('|')[0].strip()
        target_counter[target] += 1
        link_matches.append((m.start(), m.end(), full, target))
    
    flush_print(f"  Links (non-census): {len(link_matches):,}")
    
    top_targets = target_counter.most_common(DICT_SIZE)
    dictionary = {target: idx for idx, (target, _) in enumerate(top_targets)}
    coverage = sum(c for _, c in top_targets)
    flush_print(f"  Dictionary: {len(dictionary):,} entries, covers {coverage:,} links ({coverage/max(1,len(link_matches))*100:.1f}%)")
    
    link_replacements = []
    bytes_saved = 0
    for start, end, full_link, target in link_matches:
        if target not in dictionary:
            continue
        idx = dictionary[target]
        idx_bytes = struct.pack('>H', idx)
        parts = full_link.split('|', 1)
        if len(parts) > 1:
            repl = LINK_MARKER + idx_bytes + b'|' + parts[1].encode('utf-8', errors='ignore')
        else:
            repl = LINK_MARKER + idx_bytes
        if len(repl) < (end - start):
            link_replacements.append((start, end, repl))
            bytes_saved += (end - start) - len(repl)
    
    flush_print(f"  Link replacements: {len(link_replacements):,}, bytes saved: {bytes_saved:,} ({bytes_saved/1024/1024:.2f} MB)")
    return link_replacements, dictionary

# ─── Phase 3: Metadata extraction ───
def phase_metadata(data, census_ranges):
    flush_print("PHASE 3: Metadata Extraction")
    
    meta_patterns = [
        (re.compile(r'<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z</timestamp>'), b'T'),
        (re.compile(r'<contributor>\s*<username>[^<]*</username>\s*<id>\d+</id>\s*</contributor>', re.DOTALL), b'C'),
        (re.compile(r'<comment>[^<]*</comment>'), b'M'),
        (re.compile(r'<minor />\s*'), b'N'),
    ]
    
    meta_replacements = []
    meta_stream = []
    meta_idx = 0
    bytes_saved = 0
    
    for pattern, type_byte in meta_patterns:
        count = 0
        for m in pattern.finditer(data):
            # Skip if inside census article
            in_census = False
            for cs, ce, _ in census_ranges:
                if cs <= m.start() < ce:
                    in_census = True
                    break
            if in_census:
                continue
            
            idx_bytes = struct.pack('>I', meta_idx)[1:]  # 3 bytes
            repl = META_MARKER + type_byte + idx_bytes
            orig_len = m.end() - m.start()
            if len(repl) < orig_len:
                meta_replacements.append((m.start(), m.end(), repl))
                meta_stream.append(m.group(0))
                bytes_saved += orig_len - len(repl)
                meta_idx += 1
                count += 1
        flush_print(f"  {type_byte.decode()}: {count:,} entries")
    
    flush_print(f"  Metadata total: {meta_idx:,}, bytes saved: {bytes_saved:,} ({bytes_saved/1024/1024:.2f} MB)")
    return meta_replacements, meta_stream

# ─── Phase 4: Merge & Write ───
def merge_and_write(input_path, output_path, census_repls, link_repls, meta_repls, dictionary, meta_stream):
    flush_print("PHASE 4: Merge & Write")
    
    # Combine all replacements
    all_repls = census_repls + link_repls + meta_repls
    all_repls.sort(key=lambda x: x[0])
    
    # Remove overlaps
    clean = []
    prev_end = 0
    for start, end, repl in all_repls:
        if start >= prev_end:
            clean.append((start, end, repl))
            prev_end = end
    
    removed = len(all_repls) - len(clean)
    flush_print(f"  Total replacements: {len(clean):,} ({removed:,} overlaps removed)")
    
    # Free memory
    del all_repls, census_repls, link_repls, meta_repls
    import gc; gc.collect()
    
    flush_print(f"  Writing to {output_path}...")
    
    with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
        # Header
        fout.write(b'COMBINED_V1\n')
        
        # Link dictionary
        dict_items = sorted(dictionary.items(), key=lambda x: x[1])
        fout.write(struct.pack('<H', len(dict_items)))
        for target, idx in dict_items:
            tb = target.encode('utf-8')
            fout.write(struct.pack('<H', len(tb)))
            fout.write(tb)
        
        # Metadata stream
        fout.write(struct.pack('<I', len(meta_stream)))
        for entry in meta_stream:
            eb = entry.encode('utf-8')
            fout.write(struct.pack('<I', len(eb)))
            fout.write(eb)
        
        fout.write(b'\n---MAIN---\n')
        
        # Stream write with replacements
        pos = 0
        total = len(clean)
        chunk_report = max(1, total // 20)
        
        for i, (start, end, repl) in enumerate(clean):
            if start > pos:
                fin.seek(pos)
                fout.write(fin.read(start - pos))
            fout.write(repl)
            pos = end
            if (i + 1) % chunk_report == 0:
                flush_print(f"  Write progress: {(i+1)/total*100:.0f}%")
        
        # Remaining
        fin.seek(pos)
        fout.write(fin.read())
    
    final_size = os.path.getsize(output_path)
    flush_print(f"  Output: {final_size:,} bytes ({final_size/1024/1024:.2f} MB)")
    return final_size

def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else '/root/hutter/paq8px/enwik9_reordered_transformed'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/root/hutter/paq8px/enwik9_combined'
    
    flush_print("=" * 60)
    flush_print("COMBINED: Census + LinkDict + Metadata v1")
    flush_print("=" * 60)
    
    flush_print(f"\nLoading {input_path}...")
    with open(input_path, 'r', errors='ignore') as f:
        data = f.read()
    original_size = len(data)
    flush_print(f"Size: {original_size:,} bytes ({original_size/1024/1024:.1f} MB)\n")
    
    # Phase 1: Census
    census_repls = phase_census(data)
    
    # Phase 2: Links (skip census ranges)
    link_repls, dictionary = phase_links(data, census_repls)
    
    # Phase 3: Metadata (skip census ranges)
    meta_repls, meta_stream = phase_metadata(data, census_repls)
    
    # Free data before writing
    del data
    import gc; gc.collect()
    flush_print("\n  Memory freed, streaming write...\n")
    
    # Phase 4: Write
    final_size = merge_and_write(input_path, output_path, census_repls, link_repls, meta_repls, dictionary, meta_stream)
    
    flush_print(f"\n{'=' * 60}")
    flush_print("SUMMARY")
    flush_print(f"{'=' * 60}")
    flush_print(f"  Original:  {original_size:,} bytes ({original_size/1024/1024:.2f} MB)")
    flush_print(f"  Output:    {final_size:,} bytes ({final_size/1024/1024:.2f} MB)")
    flush_print(f"  Savings:   {original_size - final_size:,} bytes ({(original_size - final_size)/1024/1024:.2f} MB)")
    flush_print(f"  Ratio:     {final_size/original_size*100:.2f}%")
    flush_print(f"\n  Next: compress with paq8px -5")

if __name__ == '__main__':
    main()
