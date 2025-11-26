#!/usr/bin/env python3
"""
Wikipedia Pre-processor for Enhanced Compression

THE IDEA:
Instead of compressing Wikipedia with embedded [[links]], we:
1. Extract all links to a dictionary
2. Replace links with short IDs
3. Compress transformed text + dictionary separately
4. Reconstruct on decompression

WHY IT WORKS:
- Links are highly repetitive ("Wikipedia", "United States", etc.)
- After extraction, each link stored ONCE in dictionary
- Transformed text is shorter and more compressible
- Dictionary is tiny compared to link repetition savings

EXAMPLE:
Before: "The [[Wikipedia]] article about [[compression]] using [[Wikipedia]]..."
After:  "The ⟨1⟩ article about ⟨2⟩ using ⟨1⟩..."
Dict:   {1: "Wikipedia", 2: "compression"}
"""

import re
import sys
from collections import OrderedDict
from pathlib import Path


class WikipediaPreprocessor:
    def __init__(self):
        self.link_dict = OrderedDict()
        self.next_id = 1
        
    def extract_links(self, text):
        """
        Extract Wikipedia article links and build dictionary.
        
        Focus on simple article links, skip special ones (images, categories, etc.)
        
        Returns transformed text with links replaced by IDs.
        """
        def replace_link(match):
            full_link = match.group(0)  # [[link]] or [[link|text]]
            link_content = match.group(1)  # Just the link part
            
            # Skip special links (images, categories, files, etc.)
            if any(link_content.lower().startswith(prefix) for prefix in 
                   ['image:', 'file:', 'category:', 'template:', 'wikipedia:', 
                    'help:', 'portal:', 'wikt:', 's:']):
                return full_link  # Keep as-is
            
            # Skip if contains nested brackets (complex markup)
            if '[[' in link_content or ']]' in link_content:
                return full_link  # Keep as-is
            
            # Handle [[link|display text]] format
            if '|' in link_content:
                actual_link, display_text = link_content.split('|', 1)
                has_display = True
            else:
                actual_link = link_content
                display_text = ""
                has_display = False
            
            # Add to dictionary if new
            if actual_link not in self.link_dict.values():
                link_id = self.next_id
                self.link_dict[link_id] = actual_link
                self.next_id += 1
            else:
                # Find existing ID
                link_id = [k for k, v in self.link_dict.items() if v == actual_link][0]
            
            # Replace with ID marker, preserving display text if present
            if has_display:
                return f"⟨{link_id}|{display_text}⟩"
            else:
                return f"⟨{link_id}⟩"
        
        # Pattern matches [[link]] and [[link|display]]
        # Non-greedy match to avoid nested brackets
        pattern = r'\[\[([^\[\]]+?)\]\]'
        transformed = re.sub(pattern, replace_link, text)
        
        return transformed
    
    def save_dictionary(self, filepath):
        """Save link dictionary to file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Wikipedia Link Dictionary\n")
            f.write(f"# Total unique links: {len(self.link_dict)}\n")
            for link_id, link in self.link_dict.items():
                f.write(f"{link_id}\t{link}\n")
    
    def load_dictionary(self, filepath):
        """Load link dictionary from file."""
        self.link_dict = OrderedDict()
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    link_id = int(parts[0])
                    link = parts[1]
                    self.link_dict[link_id] = link
                    self.next_id = max(self.next_id, link_id + 1)
    
    def restore_links(self, transformed_text):
        """Restore original links from transformed text."""
        def replace_id(match):
            full_match = match.group(0)
            link_id = int(match.group(1))
            display_text = match.group(2) if match.group(2) else None
            
            if link_id in self.link_dict:
                link = self.link_dict[link_id]
                if display_text:
                    return f"[[{link}|{display_text}]]"
                else:
                    return f"[[{link}]]"
            else:
                return full_match  # Keep if not found
        
        # Pattern matches ⟨id⟩ or ⟨id|display⟩
        pattern = r'⟨(\d+)(?:\|([^⟩]+))?⟩'
        restored = re.sub(pattern, replace_id, transformed_text)
        return restored
    
    def preprocess_file(self, input_path, output_text_path, output_dict_path):
        """
        Preprocess Wikipedia file.
        
        Args:
            input_path: Original Wikipedia file
            output_text_path: Transformed text output
            output_dict_path: Dictionary output
        """
        print(f"Reading {input_path}...")
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_text = f.read()
        
        original_size = len(original_text)
        print(f"Original size: {original_size:,} bytes")
        
        print("Extracting links...")
        transformed_text = self.extract_links(original_text)
        
        print("Saving transformed text...")
        with open(output_text_path, 'w', encoding='utf-8') as f:
            f.write(transformed_text)
        
        transformed_size = len(transformed_text)
        
        print("Saving dictionary...")
        self.save_dictionary(output_dict_path)
        
        with open(output_dict_path, 'r', encoding='utf-8') as f:
            dict_size = len(f.read())
        
        print("\n" + "="*60)
        print("PRE-PROCESSING RESULTS:")
        print("="*60)
        print(f"Original size:       {original_size:,} bytes")
        print(f"Transformed size:    {transformed_size:,} bytes")
        print(f"Dictionary size:     {dict_size:,} bytes")
        print(f"Total after transform: {transformed_size + dict_size:,} bytes")
        print(f"Savings before compression: {original_size - (transformed_size + dict_size):,} bytes")
        print(f"Reduction: {100 * (1 - (transformed_size + dict_size) / original_size):.2f}%")
        print(f"\nUnique links found: {len(self.link_dict):,}")
        print("="*60)
        
        return transformed_size, dict_size
    
    def reconstruct_file(self, input_text_path, input_dict_path, output_path):
        """
        Reconstruct original file from transformed text and dictionary.
        
        Args:
            input_text_path: Transformed text file
            input_dict_path: Dictionary file
            output_path: Reconstructed output
        """
        print(f"Loading dictionary from {input_dict_path}...")
        self.load_dictionary(input_dict_path)
        
        print(f"Reading transformed text from {input_text_path}...")
        with open(input_text_path, 'r', encoding='utf-8') as f:
            transformed_text = f.read()
        
        print("Restoring links...")
        restored_text = self.restore_links(transformed_text)
        
        print(f"Writing reconstructed file to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(restored_text)
        
        print(f"\n✅ Reconstruction complete!")
        print(f"Output size: {len(restored_text):,} bytes")


def main():
    """Test the preprocessor on enwik_10mb."""
    
    print("="*60)
    print("WIKIPEDIA PRE-PROCESSOR")
    print("Novel compression enhancement through data transformation")
    print("="*60)
    print()
    
    # Test on enwik_10mb
    input_file = Path("data/enwik_10mb")
    
    if not input_file.exists():
        print(f"❌ Error: {input_file} not found!")
        return
    
    output_text = Path("data/enwik_10mb_transformed.txt")
    output_dict = Path("data/enwik_10mb_dictionary.txt")
    output_reconstructed = Path("data/enwik_10mb_reconstructed.txt")
    
    # Pre-process
    print("\n### PHASE 1: PRE-PROCESSING ###\n")
    preprocessor = WikipediaPreprocessor()
    preprocessor.preprocess_file(input_file, output_text, output_dict)
    
    # Reconstruct to verify
    print("\n### PHASE 2: VERIFICATION ###\n")
    verifier = WikipediaPreprocessor()
    verifier.reconstruct_file(output_text, output_dict, output_reconstructed)
    
    # Compare
    print("\n### PHASE 3: INTEGRITY CHECK ###\n")
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        original = f.read()
    with open(output_reconstructed, 'r', encoding='utf-8') as f:
        reconstructed = f.read()
    
    if original == reconstructed:
        print("✅ SUCCESS! Reconstruction is PERFECT!")
        print("   Pre-processing is lossless and reversible!")
    else:
        print("⚠️  WARNING: Reconstruction differs from original")
        print(f"   Original size: {len(original)}")
        print(f"   Reconstructed size: {len(reconstructed)}")
        # Find first difference
        for i, (c1, c2) in enumerate(zip(original, reconstructed)):
            if c1 != c2:
                print(f"   First difference at position {i}")
                print(f"   Original: {repr(original[max(0,i-20):i+20])}")
                print(f"   Reconstructed: {repr(reconstructed[max(0,i-20):i+20])}")
                break
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Compress transformed text with PAQ8")
    print("2. Compress dictionary (it's tiny!)")
    print("3. Compare total size with baseline")
    print("4. Calculate improvement!")
    print("="*60)


if __name__ == "__main__":
    main()
