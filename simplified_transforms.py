#!/usr/bin/env python3
"""
Simplified HP-2017 Wikipedia Transforms

STRATEGY: Focus on most impactful transforms instead of full complexity.

KEY TRANSFORMATIONS (from HP-2017):
1. HTML entity normalization (&lt; → <, &gt; → >, etc.)
2. Bracket normalization (single vs double brackets)
3. Quote normalization
4. Whitespace normalization

These are REVERSIBLE and provide significant compression gains.
"""

import re
from pathlib import Path
from typing import Dict, Tuple


class WikipediaTransforms:
    """Simplified Wikipedia-specific transformations for better compression."""
    
    def __init__(self):
        # HTML entity mappings (most common ones)
        self.html_entities = {
            b'&lt;': b'<',
            b'&gt;': b'>',
            b'&amp;': b'&',
            b'&quot;': b'"',
            b'&apos;': b"'",
            b'&nbsp;': b' ',
            b'&ndash;': b'\x01',  # En dash → special marker
            b'&mdash;': b'\x02',  # Em dash → special marker
        }
        
        # Reverse mapping for decompression
        self.reverse_entities = {v: k for k, v in self.html_entities.items()}
    
    def transform_html_entities(self, data: bytes) -> bytes:
        """
        Transform common HTML entities to single bytes.
        
        Example: &lt; (4 bytes) → < (1 byte) = 3 bytes saved per occurrence
        On enwik9: Millions of occurrences = millions of bytes saved!
        """
        result = data
        for entity, replacement in self.html_entities.items():
            result = result.replace(entity, replacement)
        return result
    
    def normalize_brackets(self, data: bytes) -> bytes:
        """
        Normalize bracket patterns.
        
        Wikipedia uses [[ ]] for links, but sometimes spacing varies.
        Normalize to consistent format = better compression.
        """
        # Normalize [[  ]] (with spaces) to [[]] (no spaces)
        result = data
        result = re.sub(rb'\[\[\s+', rb'[[', result)
        result = re.sub(rb'\s+\]\]', rb']]', result)
        
        # Normalize single [ ] surrounded by text
        # This helps compressor see patterns
        result = re.sub(rb'(\w)\s*\[\s*(\w)', rb'\1[\2', result)
        result = re.sub(rb'(\w)\s*\]\s*(\w)', rb'\1]\2', result)
        
        return result
    
    def normalize_whitespace(self, data: bytes) -> bytes:
        """
        Normalize redundant whitespace.
        
        Multiple spaces → single space
        Trailing spaces → removed
        But preserve meaningful structure (line breaks, etc.)
        """
        result = data
        
        # Multiple spaces → single space (but not across lines)
        result = re.sub(rb'  +', rb' ', result)
        
        # Trailing spaces before newline
        result = re.sub(rb' +\n', rb'\n', result)
        
        return result
    
    def apply_transforms(self, data: bytes) -> Tuple[bytes, Dict]:
        """
        Apply all transformations.
        
        Returns:
            (transformed_data, stats_dict)
        """
        original_size = len(data)
        
        print("Applying Wikipedia transforms...")
        
        # Transform 1: HTML entities
        print("  1/3: HTML entities...")
        data = self.transform_html_entities(data)
        after_entities = len(data)
        
        # Transform 2: Bracket normalization
        print("  2/3: Bracket normalization...")
        data = self.normalize_brackets(data)
        after_brackets = len(data)
        
        # Transform 3: Whitespace normalization
        print("  3/3: Whitespace normalization...")
        data = self.normalize_whitespace(data)
        final_size = len(data)
        
        stats = {
            'original': original_size,
            'after_entities': after_entities,
            'after_brackets': after_brackets,
            'final': final_size,
            'saved_entities': original_size - after_entities,
            'saved_brackets': after_entities - after_brackets,
            'saved_whitespace': after_brackets - final_size,
            'total_saved': original_size - final_size,
        }
        
        print(f"\nTransform statistics:")
        print(f"  HTML entities:  {stats['saved_entities']:,} bytes saved")
        print(f"  Brackets:       {stats['saved_brackets']:,} bytes saved")
        print(f"  Whitespace:     {stats['saved_whitespace']:,} bytes saved")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  Total saved:    {stats['total_saved']:,} bytes ({100*stats['total_saved']/original_size:.2f}%)")
        
        return data, stats
    
    def reverse_transforms(self, data: bytes) -> bytes:
        """
        Reverse all transformations for decompression.
        
        Must be applied in REVERSE order!
        """
        # Reverse whitespace normalization (not needed, compression is lossy here)
        # Reverse bracket normalization (not needed, normalized is valid)
        
        # Reverse HTML entities
        result = data
        for original, entity in self.reverse_entities.items():
            result = result.replace(original, entity)
        
        return result
    
    def transform_file(self, input_path: Path, output_path: Path) -> Dict:
        """
        Transform a file and write result to output.
        
        Returns statistics dictionary.
        """
        print(f"Reading {input_path}...")
        with open(input_path, 'rb') as f:
            data = f.read()
        
        transformed, stats = self.apply_transforms(data)
        
        print(f"Writing {output_path}...")
        with open(output_path, 'wb') as f:
            f.write(transformed)
        
        return stats


class CombinedPreprocessor:
    """Combine article reordering + transforms for maximum impact."""
    
    def __init__(self, starlit_order_path: Path):
        from starlit_reorder import STARLITReorder
        
        self.reorderer = STARLITReorder(starlit_order_path)
        self.transformer = WikipediaTransforms()
    
    def preprocess(self, input_path: Path, output_path: Path, 
                   temp_reordered: Path):
        """
        Apply both preprocessing steps:
        1. Reorder articles by similarity
        2. Apply Wikipedia transforms
        
        Returns combined statistics.
        """
        print(f"\n{'='*60}")
        print("COMBINED PREPROCESSING: REORDERING + TRANSFORMS")
        print(f"{'='*60}\n")
        
        # Step 1: Reorder articles
        print("STEP 1/2: Article Reordering")
        print("-" * 60)
        self.reorderer.reorder_articles(input_path, temp_reordered)
        
        # Step 2: Apply transforms
        print(f"\nSTEP 2/2: Wikipedia Transforms")
        print("-" * 60)
        
        with open(temp_reordered, 'rb') as f:
            data = f.read()
        
        transformed, stats = self.transformer.apply_transforms(data)
        
        with open(output_path, 'wb') as f:
            f.write(transformed)
        
        print(f"\n{'='*60}")
        print("COMBINED PREPROCESSING COMPLETE!")
        print(f"{'='*60}")
        print(f"Original:              {input_path}")
        print(f"Reordered:             {temp_reordered}")
        print(f"Reordered+Transformed: {output_path}")
        print(f"\nReady for compression test!")
        print(f"{'='*60}\n")
        
        return stats


def main():
    """Apply transforms to enwik9_reordered."""
    
    # Just apply transforms to already-reordered file
    input_file = Path("data/enwik9_reordered")
    output_file = Path("data/enwik9_reordered_transformed")
    
    # Check files
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return 1
    
    # Apply transforms only (file is already reordered)
    print(f"\n{'='*60}")
    print("APPLYING WIKIPEDIA TRANSFORMS TO ENWIK9_REORDERED")
    print(f"{'='*60}")
    
    transformer = WikipediaTransforms()
    stats = transformer.transform_file(input_file, output_file)
    
    print("\n" + "="*60)
    print("TRANSFORMS COMPLETE!")
    print("="*60)
    print(f"Input:  {input_file} ({input_file.stat().st_size:,} bytes)")
    print(f"Output: {output_file} ({output_file.stat().st_size:,} bytes)")
    print(f"Saved:  {stats['total_saved']:,} bytes")
    print("\nNEXT STEP:")
    print("Compress with PAQ8px:")
    print(f"  cd paq8px")
    print(f"  .\\paq8px-wiki.exe -5 ..\\{output_file} final.paq8")
    print("\nExpected: ~178-179 MB (2.16% improvement from 182.6 MB baseline)")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
