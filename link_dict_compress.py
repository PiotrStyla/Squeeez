#!/usr/bin/env python3
"""
Link Dictionary Compression for enwik9 (v3 - memory efficient).
Replaces repeated [[internal links]] with short dictionary codes.
Also extracts XML metadata to separate stream for better compression.
Uses chunk-based string building instead of list(data) to avoid OOM.
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

def scan_and_collect(data):
    """Collect all link and metadata match positions."""
    flush_print("Phase 1: Scanning links...")
    link_pattern = re.compile(r'\[\[([^\]]+)\]\]')
    
    target_counter = Counter()
    link_matches = []
    for m in link_pattern.finditer(data):
        full = m.group(1)
        target = full.split('|')[0].strip()
        target_counter[target] += 1
        link_matches.append((m.start(), m.end(), full, target))
    
    flush_print(f"  Links: {len(link_matches):,} total, {len(target_counter):,} unique targets")
    
    # Build dictionary
    top_targets = target_counter.most_common(DICT_SIZE)
    dictionary = {target: idx for idx, (target, _) in enumerate(top_targets)}
    coverage = sum(c for _, c in top_targets)
    flush_print(f"  Dictionary: {len(dictionary):,} entries, covers {coverage:,} links ({coverage/len(link_matches)*100:.1f}%)")

    flush_print("Phase 2: Scanning metadata...")
    meta_patterns = [
        (re.compile(r'<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z</timestamp>'), b'T'),
        (re.compile(r'<contributor>\s*<username>[^<]*</username>\s*<id>\d+</id>\s*</contributor>', re.DOTALL), b'C'),
        (re.compile(r'<comment>[^<]*</comment>'), b'M'),
        (re.compile(r'<minor />\s*'), b'N'),
    ]
    meta_matches = []
    for pattern, type_byte in meta_patterns:
        matches = list(pattern.finditer(data))
        total_b = sum(m.end() - m.start() for m in matches)
        flush_print(f"  {type_byte}: {len(matches):,} matches, {total_b:,} bytes ({total_b/1024/1024:.2f} MB)")
        for m in matches:
            meta_matches.append((m.start(), m.end(), type_byte, m.group(0)))
    
    return link_matches, dictionary, meta_matches

def build_replacements(data_len, link_matches, dictionary, meta_matches):
    """Build sorted, non-overlapping replacement list."""
    flush_print("Phase 3: Building replacements...")
    
    replacements = []  # (start, end, replacement_bytes)
    
    links_replaced = 0
    bytes_saved = 0
    for start, end, full_link, target in link_matches:
        if target not in dictionary:
            continue
        idx = dictionary[target]
        idx_bytes = struct.pack('>H', idx)  # 2-byte big-endian index
        
        parts = full_link.split('|', 1)
        if len(parts) > 1:
            repl = LINK_MARKER + idx_bytes + b'|' + parts[1].encode('utf-8', errors='ignore')
        else:
            repl = LINK_MARKER + idx_bytes
        
        original_len = end - start
        if len(repl) < original_len:
            replacements.append((start, end, repl))
            bytes_saved += original_len - len(repl)
            links_replaced += 1
    
    flush_print(f"  Link replacements: {links_replaced:,}, bytes saved: {bytes_saved:,} ({bytes_saved/1024/1024:.2f} MB)")
    
    meta_saved = 0
    meta_stream_entries = []
    meta_idx = 0
    for start, end, type_byte, content in meta_matches:
        idx_bytes = struct.pack('>I', meta_idx)[1:]  # 3-byte index
        repl = META_MARKER + type_byte + idx_bytes
        
        original_len = end - start
        if len(repl) < original_len:
            replacements.append((start, end, repl))
            meta_stream_entries.append(content)
            meta_saved += original_len - len(repl)
            meta_idx += 1
    
    flush_print(f"  Metadata replacements: {meta_idx:,}, bytes saved: {meta_saved:,} ({meta_saved/1024/1024:.2f} MB)")
    
    # Sort by position, remove overlaps
    replacements.sort(key=lambda x: x[0])
    clean = []
    prev_end = 0
    for start, end, repl in replacements:
        if start >= prev_end:
            clean.append((start, end, repl))
            prev_end = end
    
    removed = len(replacements) - len(clean)
    flush_print(f"  Clean: {len(clean):,} replacements ({removed:,} overlaps removed)")
    flush_print(f"  Total bytes saved: {bytes_saved + meta_saved:,} ({(bytes_saved + meta_saved)/1024/1024:.2f} MB)")
    
    return clean, meta_stream_entries

def apply_and_write(input_path, output_path, replacements, dictionary, meta_stream):
    """Stream through file, applying replacements and writing output directly."""
    flush_print(f"Phase 4: Writing output to {output_path}...")
    
    with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
        # Header
        fout.write(b'LINKDICT_V3\n')
        
        # Dictionary
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
        
        # Stream through file applying replacements
        pos = 0
        total = len(replacements)
        chunk_report = max(1, total // 20)
        
        for i, (start, end, repl) in enumerate(replacements):
            # Copy unchanged bytes from pos to start
            if start > pos:
                fin.seek(pos)
                fout.write(fin.read(start - pos))
            # Write replacement
            fout.write(repl)
            pos = end
            
            if (i + 1) % chunk_report == 0:
                flush_print(f"  Progress: {i+1:,}/{total:,} ({(i+1)/total*100:.0f}%)")
        
        # Copy remaining bytes
        fin.seek(pos)
        remaining = fin.read()
        fout.write(remaining)
    
    final_size = os.path.getsize(output_path)
    flush_print(f"  Output: {final_size:,} bytes ({final_size/1024/1024:.2f} MB)")
    return final_size

def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else '/root/hutter/paq8px/enwik9_reordered_transformed'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/root/hutter/paq8px/enwik9_linkdict'
    
    flush_print("=" * 60)
    flush_print("LINK DICTIONARY + METADATA COMPRESSION v3")
    flush_print("=" * 60)
    
    flush_print(f"\nLoading {input_path} into memory...")
    with open(input_path, 'r', errors='ignore') as f:
        data = f.read()
    original_size = len(data)
    flush_print(f"Size: {original_size:,} bytes ({original_size/1024/1024:.1f} MB)")
    
    # Scan
    link_matches, dictionary, meta_matches = scan_and_collect(data)
    
    # Build replacements (still in-memory, but just positions + small bytes)
    replacements, meta_stream = build_replacements(len(data), link_matches, dictionary, meta_matches)
    
    # Free the big data string before writing
    del data
    del link_matches
    del meta_matches
    import gc; gc.collect()
    flush_print("  Freed in-memory data, switching to streaming write...")
    
    # Stream write
    final_size = apply_and_write(input_path, output_path, replacements, dictionary, meta_stream)
    
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
