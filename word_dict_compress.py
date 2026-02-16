#!/usr/bin/env python3
"""
Word-Level Dictionary Preprocessing for enwik9.

CRAZY IDEA: PAQ models bytes in context. Order-14 = 14 chars ≈ 3 words.
If we encode top words as 1-2 byte tokens, order-14 covers 7-14 words.
This is like giving PAQ an LLM tokenizer.

Encoding:
  0x01 + 1 byte  = top 255 words (index 1-255)
  0x02 + 2 bytes = words 256-65535 (up to 65280 more)
  
Words not in dictionary stay as raw text.
"""
import re
import struct
import sys
import os
from collections import Counter

def flush_print(msg):
    print(msg, flush=True)

ESCAPE1 = 0x01  # prefix for 1-byte index
ESCAPE2 = 0x02  # prefix for 2-byte index

def scan_words(data):
    """Scan for word frequencies. Words = sequences of letters."""
    word_pat = re.compile(rb'[a-zA-Z]+')
    counter = Counter()
    for m in word_pat.finditer(data):
        w = m.group()
        if len(w) >= 3:  # only words 3+ chars (shorter ones don't save space)
            counter[w] += 1
    return counter

def build_dictionary(counter, max_entries=8192):
    """Build dictionary of most frequent words that save bytes."""
    savings = []
    for word, count in counter.items():
        wlen = len(word)
        if count >= 5:
            # 1-byte encoding: escape(1) + index(1) = 2 bytes, saves wlen-2
            # 2-byte encoding: escape(1) + index(2) = 3 bytes, saves wlen-3
            idx = len(savings)
            if idx < 255:
                save_per = wlen - 2
            else:
                save_per = wlen - 3
            if save_per > 0:
                total_save = save_per * count
                savings.append((word, count, total_save))
    
    # Sort by total savings descending
    savings.sort(key=lambda x: -x[2])
    
    # Take top entries
    dictionary = {}
    total_saved = 0
    for i, (word, count, save) in enumerate(savings[:max_entries]):
        dictionary[word] = i
        total_saved += save
    
    return dictionary, total_saved

def encode_file(data, dictionary):
    """Replace words with dictionary codes using streaming."""
    word_pat = re.compile(rb'[a-zA-Z]+')
    
    # Build reverse lookup: word -> (escape_byte, index_bytes)
    codes = {}
    for word, idx in dictionary.items():
        if idx < 255:
            codes[word] = bytes([ESCAPE1, idx + 1])
        else:
            adj = idx - 255
            codes[word] = bytes([ESCAPE2]) + struct.pack('>H', adj)
    
    # First: escape existing ESCAPE1 and ESCAPE2 bytes
    # Replace 0x01 with 0x01 0x00 and 0x02 with 0x02 0x00 0x00
    
    result = bytearray()
    pos = 0
    matches = list(word_pat.finditer(data))
    
    flush_print(f"  Encoding {len(matches):,} word positions...")
    
    replaced = 0
    for i, m in enumerate(matches):
        # Copy non-word bytes before this match, escaping special bytes
        segment = data[pos:m.start()]
        for b in segment:
            if b == ESCAPE1:
                result.append(ESCAPE1)
                result.append(0x00)
            elif b == ESCAPE2:
                result.append(ESCAPE2)
                result.append(0x00)
                result.append(0x00)
            else:
                result.append(b)
        
        word = m.group()
        if word in codes:
            result.extend(codes[word])
            replaced += 1
        else:
            result.extend(word)
        
        pos = m.end()
        
        if (i + 1) % 5000000 == 0:
            flush_print(f"    Progress: {(i+1)/len(matches)*100:.0f}%")
    
    # Copy remaining
    segment = data[pos:]
    for b in segment:
        if b == ESCAPE1:
            result.append(ESCAPE1)
            result.append(0x00)
        elif b == ESCAPE2:
            result.append(ESCAPE2)
            result.append(0x00)
            result.append(0x00)
        else:
            result.append(b)
    
    flush_print(f"  Words replaced: {replaced:,}")
    return bytes(result)

def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else '/root/hutter/paq8px/enwik9_starlit'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/root/hutter/paq8px/enwik9_worddict'
    max_words = int(sys.argv[3]) if len(sys.argv) > 3 else 8192
    
    flush_print("=" * 60)
    flush_print(f"WORD-LEVEL DICTIONARY — top {max_words} words")
    flush_print("=" * 60)
    
    flush_print(f"\nLoading {input_path}...")
    with open(input_path, 'rb') as f:
        data = f.read()
    original_size = len(data)
    flush_print(f"Original: {original_size:,} bytes ({original_size/1024/1024:.1f} MB)")
    
    flush_print("\nPhase 1: Scanning words...")
    counter = scan_words(data)
    flush_print(f"  Unique words (3+ chars): {len(counter):,}")
    flush_print(f"  Top 10 words:")
    for word, count in counter.most_common(10):
        flush_print(f"    {word.decode():20s} {count:>10,} × {len(word)} bytes = {count*len(word):>12,} bytes")
    
    flush_print(f"\nPhase 2: Building dictionary (max {max_words})...")
    dictionary, est_savings = build_dictionary(counter, max_words)
    flush_print(f"  Dictionary entries: {len(dictionary):,}")
    flush_print(f"  Estimated raw savings: {est_savings:,} bytes ({est_savings/1024/1024:.1f} MB)")
    
    flush_print(f"\nPhase 3: Encoding...")
    encoded = encode_file(data, dictionary)
    
    del data
    import gc; gc.collect()
    
    flush_print(f"\nPhase 4: Writing {output_path}...")
    with open(output_path, 'wb') as f:
        # Header
        f.write(b'WDICT_V1\n')
        f.write(struct.pack('<H', len(dictionary)))
        
        # Dictionary: sorted by index
        dict_items = sorted(dictionary.items(), key=lambda x: x[1])
        for word, idx in dict_items:
            f.write(struct.pack('<H', len(word)))
            f.write(word)
        
        f.write(b'\n---DATA---\n')
        f.write(encoded)
    
    final_size = os.path.getsize(output_path)
    flush_print(f"\n{'=' * 60}")
    flush_print(f"SUMMARY")
    flush_print(f"{'=' * 60}")
    flush_print(f"  Original:  {original_size:,} bytes ({original_size/1024/1024:.2f} MB)")
    flush_print(f"  Output:    {final_size:,} bytes ({final_size/1024/1024:.2f} MB)")
    flush_print(f"  Savings:   {original_size - final_size:,} bytes ({(original_size - final_size)/1024/1024:.2f} MB)")
    flush_print(f"  Ratio:     {final_size/original_size*100:.2f}%")
    flush_print(f"\nNext: compress with paq8px -5")

if __name__ == '__main__':
    main()
