#!/usr/bin/env python3
"""
BPE (Byte Pair Encoding) Preprocessing for enwik9.

CRAZY IDEA: Standard compressors model individual bytes.
BPE creates "super-bytes" - each representing a frequent pair.
This effectively DOUBLES PAQ's context window because order-14
now covers ~28 original characters instead of 14.

Nobody has tried BPE as preprocessing before PAQ8PX/cmix.
"""
import struct
import sys
import os
from collections import Counter

def flush_print(msg):
    print(msg, flush=True)

def count_pairs(data):
    """Count all adjacent byte pairs."""
    pairs = Counter()
    for i in range(len(data) - 1):
        pairs[(data[i], data[i+1])] += 1
    return pairs

def replace_pair(data, pair, new_byte):
    """Replace all occurrences of pair with new_byte."""
    result = bytearray()
    i = 0
    while i < len(data):
        if i < len(data) - 1 and data[i] == pair[0] and data[i+1] == pair[1]:
            result.append(new_byte)
            i += 2
        else:
            result.append(data[i])
            i += 1
    return bytes(result)

def find_unused_bytes(data):
    """Find byte values not present in data."""
    used = set(data)
    unused = []
    # Prefer high byte values (128-255) to not conflict with ASCII
    for b in range(255, -1, -1):
        if b not in used:
            unused.append(b)
    return unused

def bpe_encode(input_path, output_path, num_merges=128):
    """Apply BPE encoding to file."""
    flush_print(f"Loading {input_path}...")
    with open(input_path, 'rb') as f:
        data = f.read()
    original_size = len(data)
    flush_print(f"Original: {original_size:,} bytes ({original_size/1024/1024:.1f} MB)")
    
    # Find unused bytes
    unused = find_unused_bytes(data)
    flush_print(f"Unused byte values available: {len(unused)}")
    
    actual_merges = min(num_merges, len(unused))
    flush_print(f"Planned merges: {actual_merges}")
    
    merge_table = []  # (new_byte, byte1, byte2, count)
    
    for step in range(actual_merges):
        # Count pairs
        pairs = count_pairs(data)
        if not pairs:
            break
        
        # Find most frequent pair
        best_pair, best_count = pairs.most_common(1)[0]
        
        if best_count < 10:  # Not worth replacing if rare
            flush_print(f"  Step {step}: best pair has only {best_count} occurrences, stopping")
            break
        
        new_byte = unused[step]
        
        # Replace
        old_len = len(data)
        data = replace_pair(data, best_pair, new_byte)
        saved = old_len - len(data)
        
        merge_table.append((new_byte, best_pair[0], best_pair[1], best_count))
        
        if (step + 1) % 10 == 0 or step < 5:
            pair_repr = f"({best_pair[0]:3d},{best_pair[1]:3d})"
            try:
                pair_chars = f"'{chr(best_pair[0])}{chr(best_pair[1])}'"
            except:
                pair_chars = "??"
            flush_print(f"  Step {step+1:3d}/{actual_merges}: {pair_repr} {pair_chars:8s} count={best_count:>8,} saved={saved:>8,} bytes, total={len(data):>12,}")
    
    flush_print(f"\nMerges applied: {len(merge_table)}")
    flush_print(f"Final size: {len(data):,} bytes ({len(data)/1024/1024:.1f} MB)")
    flush_print(f"Savings: {original_size - len(data):,} bytes ({(original_size - len(data))/1024/1024:.1f} MB)")
    
    # Write output: header + merge table + data
    flush_print(f"Writing to {output_path}...")
    with open(output_path, 'wb') as f:
        f.write(b'BPE_V1\n')
        f.write(struct.pack('<H', len(merge_table)))
        for new_byte, b1, b2, count in merge_table:
            f.write(struct.pack('BBB', new_byte, b1, b2))
        f.write(b'\n---DATA---\n')
        f.write(data)
    
    final_size = os.path.getsize(output_path)
    flush_print(f"Output file: {final_size:,} bytes ({final_size/1024/1024:.1f} MB)")
    flush_print(f"Total savings: {original_size - final_size:,} bytes ({(original_size - final_size)/1024/1024:.2f} MB)")
    
    return final_size

def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else '/root/hutter/paq8px/enwik9_reordered_transformed'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/root/hutter/paq8px/enwik9_bpe'
    num_merges = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    
    flush_print("=" * 60)
    flush_print(f"BPE PREPROCESSING — {num_merges} merges")
    flush_print("=" * 60)
    
    bpe_encode(input_path, output_path, num_merges)
    
    flush_print(f"\nNext: compress with paq8px -5 or cmix")

if __name__ == '__main__':
    main()
