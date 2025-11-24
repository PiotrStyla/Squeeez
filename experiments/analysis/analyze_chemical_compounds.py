#!/usr/bin/env python3
"""
CHEMICAL COMPOUNDS ANALYSIS

Piotr's brilliant insight:
"chlorophyll" → CAS: 479-61-8 (structured!)

Question: How many chemical compounds in Wikipedia?
Could this be bigger than geographic names?
"""
import re
from collections import Counter

def analyze_chemical_content(filename):
    """Analyze chemical compounds and scientific terms"""
    
    print("=" * 70)
    print("🧪 CHEMICAL COMPOUNDS ANALYSIS")
    print("=" * 70)
    print("\nPiotr's insight: Chemical names → structured representation")
    print("(CAS numbers, formulas, masses...)\n")
    
    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print("File not found!")
        return
    
    text = data.decode('utf-8', errors='ignore')
    size_mb = len(data) / (1024 * 1024)
    
    print(f"Dataset: {size_mb:.1f} MB ({len(data):,} bytes)\n")
    
    # Extract all words
    all_words = re.findall(r'\b\w+\b', text.lower())
    word_freq = Counter(all_words)
    unique_words = len(word_freq)
    
    print(f"Baseline: {unique_words:,} unique words\n")
    
    # === CHEMICAL ANALYSIS ===
    
    print("=" * 70)
    print("🔬 FINDING CHEMICAL PATTERNS...")
    print("=" * 70)
    
    chem_stats = {
        'chemical_formulas': set(),
        'element_names': set(),
        'common_compounds': set(),
        'chemical_suffixes': set(),
        'cas_numbers': set(),
        'scientific_terms': set(),
    }
    
    # 1. Chemical formulas (e.g., H₂O, CO₂, C₅₅H₇₂MgN₄O₅)
    print("\n1️⃣ Chemical Formulas:")
    
    # Simple formulas
    formula_pattern = re.compile(r'\b[A-Z][a-z]?(?:\d+|₀|₁|₂|₃|₄|₅|₆|₇|₈|₉)+(?:[A-Z][a-z]?(?:\d+|₀|₁|₂|₃|₄|₅|₆|₇|₈|₉)+)*\b')
    formulas = formula_pattern.findall(text)
    chem_stats['chemical_formulas'].update(formulas)
    
    print(f"   Found: {len(chem_stats['chemical_formulas'])} formulas")
    if chem_stats['chemical_formulas']:
        sample = list(chem_stats['chemical_formulas'])[:10]
        print(f"   Sample: {', '.join(sample)}")
    
    # 2. Chemical element names
    print("\n2️⃣ Chemical Elements:")
    
    elements = [
        'hydrogen', 'helium', 'lithium', 'carbon', 'nitrogen', 'oxygen',
        'fluorine', 'sodium', 'magnesium', 'aluminum', 'silicon', 'phosphorus',
        'sulfur', 'chlorine', 'potassium', 'calcium', 'iron', 'copper',
        'zinc', 'silver', 'gold', 'mercury', 'lead', 'uranium'
    ]
    
    for element in elements:
        if element in text.lower():
            chem_stats['element_names'].add(element)
    
    print(f"   Found: {len(chem_stats['element_names'])} elements")
    if chem_stats['element_names']:
        sample = list(chem_stats['element_names'])[:15]
        print(f"   Sample: {', '.join(sample)}")
    
    # 3. Common chemical compounds (by name)
    print("\n3️⃣ Common Chemical Compounds:")
    
    compounds = [
        'water', 'carbon dioxide', 'methane', 'ethanol', 'glucose',
        'oxygen', 'hydrogen', 'ammonia', 'sulfuric acid',
        'chlorophyll', 'hemoglobin', 'protein', 'enzyme',
        'acid', 'base', 'salt', 'oxide', 'hydroxide'
    ]
    
    for compound in compounds:
        if compound in text.lower():
            chem_stats['common_compounds'].add(compound)
    
    print(f"   Found: {len(chem_stats['common_compounds'])} common compounds")
    if chem_stats['common_compounds']:
        sample = list(chem_stats['common_compounds'])[:10]
        print(f"   Sample: {', '.join(sample)}")
    
    # 4. Chemical suffixes (-ine, -ide, -ate, -ene, etc.)
    print("\n4️⃣ Chemical Naming Patterns (suffixes):")
    
    chem_suffix_patterns = [
        r'\b\w+ine\b',   # chlorine, caffeine
        r'\b\w+ide\b',   # oxide, chloride
        r'\b\w+ate\b',   # sulfate, nitrate
        r'\b\w+ene\b',   # benzene, ethylene
        r'\b\w+ose\b',   # glucose, fructose
        r'\b\w+ol\b',    # ethanol, methanol
        r'\b\w+yl\b',    # methyl, ethyl
    ]
    
    for pattern_str in chem_suffix_patterns:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        matches = pattern.findall(text)
        # Filter to likely chemical terms (length > 5)
        matches = [m for m in matches if len(m) > 5 and not m.lower() in ['online', 'define', 'arine']]
        chem_stats['chemical_suffixes'].update(matches[:100])  # Limit
    
    print(f"   Found: {len(chem_stats['chemical_suffixes'])} words with chemical suffixes")
    if chem_stats['chemical_suffixes']:
        sample = list(chem_stats['chemical_suffixes'])[:15]
        print(f"   Sample: {', '.join(sample)}")
    
    # 5. CAS numbers (XXX-XX-X format)
    print("\n5️⃣ CAS Numbers (e.g., 479-61-8):")
    
    cas_pattern = re.compile(r'\b\d{2,7}-\d{2}-\d\b')
    cas_numbers = cas_pattern.findall(text)
    chem_stats['cas_numbers'].update(cas_numbers)
    
    print(f"   Found: {len(chem_stats['cas_numbers'])} CAS numbers")
    if chem_stats['cas_numbers']:
        sample = list(chem_stats['cas_numbers'])[:10]
        print(f"   Sample: {', '.join(sample)}")
    
    # 6. Scientific/chemical terms
    print("\n6️⃣ Scientific Terms (bio/chem):")
    
    sci_terms = [
        'molecule', 'atom', 'ion', 'electron', 'proton', 'neutron',
        'reaction', 'synthesis', 'catalyst', 'solution',
        'photosynthesis', 'metabolism', 'enzyme', 'protein',
        'dna', 'rna', 'gene', 'cell', 'membrane'
    ]
    
    for term in sci_terms:
        if term in text.lower():
            chem_stats['scientific_terms'].add(term)
    
    print(f"   Found: {len(chem_stats['scientific_terms'])} scientific terms")
    if chem_stats['scientific_terms']:
        sample = list(chem_stats['scientific_terms'])[:10]
        print(f"   Sample: {', '.join(sample)}")
    
    # === TOTAL CALCULATION ===
    
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    total_chem = sum(len(s) for s in chem_stats.values())
    
    print(f"\nTotal unique chemical-related terms: {total_chem:,}")
    print(f"  Formulas: {len(chem_stats['chemical_formulas']):,}")
    print(f"  Elements: {len(chem_stats['element_names']):,}")
    print(f"  Common compounds: {len(chem_stats['common_compounds']):,}")
    print(f"  Chemical suffixes: {len(chem_stats['chemical_suffixes']):,}")
    print(f"  CAS numbers: {len(chem_stats['cas_numbers']):,}")
    print(f"  Scientific terms: {len(chem_stats['scientific_terms']):,}")
    
    # Percentage
    chem_percentage = (total_chem / unique_words) * 100
    
    print(f"\n🎯 KEY METRICS:")
    print(f"  Chemical terms: {total_chem:,} unique")
    print(f"  All unique words: {unique_words:,}")
    print(f"  Percentage: {chem_percentage:.1f}%")
    
    # Compare to geography
    print(f"\n🗺️  vs 🧪 COMPARISON:")
    print(f"  Geographic names: 855 (0.9%)")
    print(f"  Chemical terms: {total_chem:,} ({chem_percentage:.1f}%)")
    
    if total_chem > 855:
        ratio = total_chem / 855
        print(f"  → Chemistry is {ratio:.1f}x MORE than geography! 🔥")
    else:
        print(f"  → Chemistry is smaller than geography")
    
    # Compression potential
    print(f"\n🎯 COMPRESSION POTENTIAL:")
    
    avg_chem_length = 12  # "chlorophyll", "photosynthesis"
    avg_structured_length = 8  # "479-61-8", "C5H7O2"
    
    current_bytes = total_chem * avg_chem_length
    structured_bytes = total_chem * avg_structured_length
    potential_saving = current_bytes - structured_bytes
    
    print(f"  Current (text): ~{current_bytes:,} bytes")
    print(f"  Structured (CAS/formula): ~{structured_bytes:,} bytes")
    print(f"  Potential saving: ~{potential_saving:,} bytes = {potential_saving/1024:.1f} KB")
    
    # Extrapolate
    print(f"\n🌍 EXTRAPOLATED TO FULL ENWIK9 (1 GB):")
    scale = 1000 / size_mb
    full_saving = potential_saving * scale
    print(f"  Potential saving: ~{full_saving/1024/1024:.2f} MB")
    
    # Answer
    print("\n" + "=" * 70)
    print("💡 ANSWER")
    print("=" * 70)
    
    print(f'\n"Ile chemical compounds w Wikipedia?"')
    print(f"\n→ {total_chem:,} chemical-related terms ({chem_percentage:.1f}%)")
    
    if chem_percentage >= 2:
        print(f"\n✅ BIGGER than geography ({chem_percentage:.1f}% vs 0.9%)!")
        print(f"   Text → Structured encoding could help!")
    else:
        print(f"\n➖ Similar to geography, still small contributor")
    
    print(f"\n📝 Chemical compression strategies:")
    print(f"  1. CAS numbers: '479-61-8' (standard identifier)")
    print(f"  2. Chemical formulas: 'C₅₅H₇₂MgN₄O₅' (structured)")
    print(f"  3. Common suffixes: -ine, -ide, -ate, -ene, -ose")
    print(f"  4. Element abbreviations: Mg, Ca, Fe, Au")
    print(f"  5. Database of common compounds (top 1000)")
    
    print(f"\n🎯 Piotr's insight:")
    print(f"  'chlorophyll' (11 chars) → '479-61-8' (8 chars)")
    print(f"  Or: C₅₅H₇₂MgN₄O₅ (structured, compresses better!)")
    print(f"  = Converting TEXT to STRUCTURED DATA!")
    print(f"  = Same principle as geography → coordinates!")
    
    print("\n" + "=" * 70)
    
    return chem_stats

if __name__ == "__main__":
    stats = analyze_chemical_content("data/enwik_10mb")
    
    print("\n✨ Chemical analysis complete!")
    print("🎯 Piotr's pattern: Text → Structured = Better compression! 🏆")
