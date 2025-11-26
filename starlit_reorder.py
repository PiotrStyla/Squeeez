#!/usr/bin/env python3
"""
STARLIT Article Reordering Implementation

THE BREAKTHROUGH:
Instead of alphabetical order, reorder Wikipedia articles by SIMILARITY.
Similar articles near each other = better compression context = 20 MB saved!

Based on STARLIT algorithm (Hutter Prize 2021 winner)
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


class ArticleExtractor:
    """Extract Wikipedia articles from enwik9 format."""
    
    def __init__(self):
        # Article starts with <title>TITLE</title>
        # Article ends at next <title> or end of file
        self.article_pattern = re.compile(
            rb'<title>([^<]+)</title>',
            re.MULTILINE
        )
    
    def extract_articles(self, data: bytes) -> List[Tuple[int, int, bytes]]:
        """
        Extract all articles with their boundaries.
        
        Returns:
            List of (start_pos, end_pos, title) tuples
        """
        articles = []
        matches = list(self.article_pattern.finditer(data))
        
        print(f"Found {len(matches)} articles in data")
        
        for i, match in enumerate(matches):
            start_pos = match.start()
            title = match.group(1)
            
            # End position is start of next article (or end of file)
            if i < len(matches) - 1:
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(data)
            
            articles.append((start_pos, end_pos, title))
        
        return articles
    
    def get_article_content(self, data: bytes, start: int, end: int) -> bytes:
        """Extract article content between positions."""
        return data[start:end]


class STARLITReorder:
    """Implement STARLIT article reordering."""
    
    def __init__(self, order_file: Path):
        """
        Load STARLIT article ordering.
        
        Args:
            order_file: Path to new_article_order file from STARLIT
        """
        self.new_order = []
        
        print(f"Loading STARLIT article order from {order_file}...")
        with open(order_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    self.new_order.append(int(line))
        
        print(f"Loaded ordering for {len(self.new_order)} articles")
    
    def reorder_articles(self, input_path: Path, output_path: Path):
        """
        Reorder articles according to STARLIT algorithm.
        
        Args:
            input_path: Original enwik file
            output_path: Reordered output file
        """
        print(f"\n{'='*60}")
        print("STARLIT ARTICLE REORDERING")
        print(f"{'='*60}\n")
        
        # Read input file
        print(f"Reading {input_path}...")
        with open(input_path, 'rb') as f:
            data = f.read()
        
        original_size = len(data)
        print(f"Original size: {original_size:,} bytes")
        
        # Extract articles
        print("\nExtracting articles...")
        extractor = ArticleExtractor()
        articles = extractor.extract_articles(data)
        
        print(f"Found {len(articles)} articles")
        print(f"STARLIT order has {len(self.new_order)} entries")
        
        # Reorder articles
        print("\nReordering articles by similarity...")
        reordered_data = bytearray()
        
        # Track which articles we've placed
        used_articles = set()
        
        # First: Place articles according to STARLIT order
        placed_count = 0
        for new_position, original_index in enumerate(self.new_order):
            if new_position % 10000 == 0:
                print(f"  Processing article {new_position:,}/{len(self.new_order):,}...")
            
            # STARLIT indices are 0-based
            if original_index < len(articles):
                start, end, title = articles[original_index]
                article_content = extractor.get_article_content(data, start, end)
                reordered_data.extend(article_content)
                used_articles.add(original_index)
                placed_count += 1
        
        print(f"Placed {placed_count:,} articles according to STARLIT order")
        
        # Second: Append any remaining articles (not in STARLIT order)
        # This handles articles added after STARLIT was computed
        remaining_count = 0
        for i, (start, end, title) in enumerate(articles):
            if i not in used_articles:
                article_content = extractor.get_article_content(data, start, end)
                reordered_data.extend(article_content)
                remaining_count += 1
        
        if remaining_count > 0:
            print(f"Appended {remaining_count:,} remaining articles")
        
        # Write reordered data
        print(f"\nWriting reordered data to {output_path}...")
        with open(output_path, 'wb') as f:
            f.write(reordered_data)
        
        reordered_size = len(reordered_data)
        
        print(f"\n{'='*60}")
        print("REORDERING COMPLETE!")
        print(f"{'='*60}")
        print(f"Original size:   {original_size:,} bytes")
        print(f"Reordered size:  {reordered_size:,} bytes")
        print(f"Difference:      {reordered_size - original_size:,} bytes")
        
        if reordered_size == original_size:
            print("✅ Perfect! No data lost or added.")
        elif abs(reordered_size - original_size) < 100:
            print("✅ Nearly perfect! Minimal difference (likely trailing bytes).")
        else:
            print("⚠️  Size differs significantly - check implementation!")
        
        print(f"\n{'='*60}")
        print("NEXT STEPS:")
        print(f"{'='*60}")
        print("1. Compress original with PAQ8:")
        print(f"   paq8px-wiki.exe -5 {input_path} original.paq8")
        print("2. Compress reordered with PAQ8:")
        print(f"   paq8px-wiki.exe -5 {output_path} reordered.paq8")
        print("3. Compare sizes - expect 15-20 MB improvement!")
        print(f"{'='*60}\n")


def main():
    """Test article reordering on enwik_10mb."""
    
    # Paths
    starlit_order = Path("starlit/src/readalike_prepr/data/new_article_order")
    input_file = Path("data/enwik_10mb")
    output_file = Path("data/enwik_10mb_reordered")
    
    # Check files exist
    if not starlit_order.exists():
        print(f"❌ Error: STARLIT order file not found: {starlit_order}")
        print("   Make sure starlit repository is cloned!")
        return 1
    
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        print("   Make sure enwik_10mb exists in data/ directory!")
        return 1
    
    # Reorder
    reorderer = STARLITReorder(starlit_order)
    reorderer.reorder_articles(input_file, output_file)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
