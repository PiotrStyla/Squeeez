#!/usr/bin/env python3
"""
DEEP geographic analysis with real pattern matching
Better answer to: "Ile maskotek to nazwy geograficzne?"
"""
import re
from collections import Counter

def analyze_real_geographic_content(filename):
    """More sophisticated geographic analysis"""
    
    print("=" * 70)
    print("🗺️  DEEP GEOGRAPHIC ANALYSIS")
    print("=" * 70)
    
    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print("File not found!")
        return
    
    text = data.decode('utf-8', errors='ignore')
    size_mb = len(data) / (1024 * 1024)
    
    print(f"\nDataset: {size_mb:.1f} MB ({len(data):,} bytes)\n")
    
    # Extract all words (for baseline)
    all_words = re.findall(r'\b\w+\b', text.lower())
    word_freq = Counter(all_words)
    
    total_words = len(all_words)
    unique_words = len(word_freq)
    
    print(f"Total words: {total_words:,}")
    print(f"Unique words: {unique_words:,}\n")
    
    # === GEOGRAPHIC ANALYSIS ===
    
    print("=" * 70)
    print("🌍 FINDING GEOGRAPHIC NAMES...")
    print("=" * 70)
    
    geo_stats = {
        'cities': set(),
        'countries': set(),
        'regions': set(),
        'rivers': set(),
        'mountains': set(),
        'other_places': set(),
    }
    
    # 1. Common geographic keywords in context
    print("\n1️⃣ Cities (from common patterns):")
    
    # Cities often appear with these patterns
    city_contexts = [
        r'city\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s+a\s+city',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+is\s+the\s+capital',
    ]
    
    for pattern in city_contexts:
        matches = re.findall(pattern, text)
        geo_stats['cities'].update(matches)
    
    # Also find words with city suffixes
    city_suffixes = ['burg', 'ville', 'ton', 'ford', 'ham', 'port', 'polis']
    capitalized = re.findall(r'\b[A-Z][a-z]{3,}(?:burg|ville|ton|ford|ham|port|polis)\b', text)
    geo_stats['cities'].update(capitalized)
    
    print(f"   Found: {len(geo_stats['cities'])} unique cities")
    if geo_stats['cities']:
        sample = list(geo_stats['cities'])[:15]
        print(f"   Sample: {', '.join(sample)}")
    
    # 2. Countries
    print("\n2️⃣ Countries:")
    
    # Common country names (top 50)
    known_countries = [
        'Afghanistan', 'Albania', 'Algeria', 'Argentina', 'Australia',
        'Austria', 'Belgium', 'Brazil', 'Bulgaria', 'Canada',
        'Chile', 'China', 'Colombia', 'Croatia', 'Cuba',
        'Denmark', 'Egypt', 'England', 'Ethiopia', 'Finland',
        'France', 'Germany', 'Greece', 'Hungary', 'Iceland',
        'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland',
        'Israel', 'Italy', 'Japan', 'Jordan', 'Kenya',
        'Korea', 'Mexico', 'Netherlands', 'Nigeria', 'Norway',
        'Pakistan', 'Poland', 'Portugal', 'Romania', 'Russia',
        'Serbia', 'Spain', 'Sweden', 'Switzerland', 'Syria',
        'Thailand', 'Turkey', 'Ukraine', 'Vietnam',
    ]
    
    for country in known_countries:
        if country in text:
            geo_stats['countries'].add(country)
    
    # Also find -land, -stan countries
    country_suffixes = re.findall(r'\b[A-Z][a-z]{3,}(?:land|stan)\b', text)
    geo_stats['countries'].update(country_suffixes)
    
    print(f"   Found: {len(geo_stats['countries'])} unique countries")
    if geo_stats['countries']:
        sample = list(geo_stats['countries'])[:20]
        print(f"   Sample: {', '.join(sample)}")
    
    # 3. Rivers
    print("\n3️⃣ Rivers:")
    
    river_pattern = re.compile(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+[Rr]iver')
    rivers = river_pattern.findall(text)
    geo_stats['rivers'].update(rivers)
    
    # Also "River X"
    river_pattern2 = re.compile(r'[Rr]iver\s+([A-Z][a-z]+)')
    rivers2 = river_pattern2.findall(text)
    geo_stats['rivers'].update(rivers2)
    
    print(f"   Found: {len(geo_stats['rivers'])} unique rivers")
    if geo_stats['rivers']:
        sample = list(geo_stats['rivers'])[:10]
        print(f"   Sample: {', '.join(sample)}")
    
    # 4. Mountains
    print("\n4️⃣ Mountains:")
    
    mountain_pattern = re.compile(r'(?:Mount|Mt\.)\s+([A-Z][a-z]+)')
    mountains = mountain_pattern.findall(text)
    geo_stats['mountains'].update(mountains)
    
    # "X Mountain"
    mountain_pattern2 = re.compile(r'([A-Z][a-z]+)\s+Mountain')
    mountains2 = mountain_pattern2.findall(text)
    geo_stats['mountains'].update(mountains2)
    
    print(f"   Found: {len(geo_stats['mountains'])} unique mountains")
    if geo_stats['mountains']:
        sample = list(geo_stats['mountains'])[:10]
        print(f"   Sample: {', '.join(sample)}")
    
    # 5. US States (common ones)
    print("\n5️⃣ US States & Regions:")
    
    us_states = [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
        'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
        'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
        'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
        'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri',
        'Montana', 'Nebraska', 'Nevada', 'Hampshire', 'Jersey',
        'Mexico', 'York', 'Carolina', 'Dakota', 'Ohio',
        'Oklahoma', 'Oregon', 'Pennsylvania', 'Island', 'Tennessee',
        'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
        'Wisconsin', 'Wyoming'
    ]
    
    states_found = set()
    for state in us_states:
        if state in text:
            states_found.add(state)
    
    geo_stats['regions'].update(states_found)
    
    print(f"   Found: {len(states_found)} US states/regions")
    if states_found:
        sample = list(states_found)[:15]
        print(f"   Sample: {', '.join(sample)}")
    
    # === TOTAL CALCULATION ===
    
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    total_geo_names = sum(len(s) for s in geo_stats.values())
    
    print(f"\nTotal unique geographic names found: {total_geo_names:,}")
    print(f"  Cities: {len(geo_stats['cities']):,}")
    print(f"  Countries: {len(geo_stats['countries']):,}")
    print(f"  US States/Regions: {len(geo_stats['regions']):,}")
    print(f"  Rivers: {len(geo_stats['rivers']):,}")
    print(f"  Mountains: {len(geo_stats['mountains']):,}")
    
    # Percentage of unique words
    geo_percentage = (total_geo_names / unique_words) * 100
    
    print(f"\n🎯 KEY METRICS:")
    print(f"  Geographic names: {total_geo_names:,} unique")
    print(f"  All unique words: {unique_words:,}")
    print(f"  Percentage: {geo_percentage:.1f}%")
    
    # Estimate bytes
    avg_name_length = 10  # "California", "Mississippi", "New York"
    total_geo_bytes = total_geo_names * avg_name_length
    geo_bytes_percentage = (total_geo_bytes / len(data)) * 100
    
    print(f"\n💾 SIZE ESTIMATE:")
    print(f"  Avg geo name length: ~{avg_name_length} chars")
    print(f"  Total geo bytes: ~{total_geo_bytes:,} bytes")
    print(f"  As % of {size_mb:.0f} MB: ~{geo_bytes_percentage:.2f}%")
    
    # Compression potential
    print(f"\n🎯 COMPRESSION POTENTIAL:")
    
    # Current: each name encoded fully
    # Better: hierarchical encoding
    
    savings_scenarios = {
        '10% better': total_geo_bytes * 0.10,
        '25% better': total_geo_bytes * 0.25,
        '50% better': total_geo_bytes * 0.50,
    }
    
    for scenario, saving in savings_scenarios.items():
        kb_saved = saving / 1024
        print(f"  {scenario}: ~{kb_saved:.0f} KB saved")
    
    # Extrapolate to full enwik9
    print(f"\n🌍 EXTRAPOLATED TO FULL ENWIK9 (1 GB):")
    
    scale_factor = 1000 / size_mb  # enwik9 is ~1GB, we have 10MB
    full_geo_bytes = total_geo_bytes * scale_factor
    
    print(f"  Estimated geo bytes in enwik9: ~{full_geo_bytes/1024/1024:.1f} MB")
    print(f"  If 50% better compression: ~{(full_geo_bytes*0.5)/1024/1024:.2f} MB saved")
    
    # Answer the question!
    print("\n" + "=" * 70)
    print("💡 ANSWER TO QUESTION")
    print("=" * 70)
    
    print(f'\n"Ile z tych maskotek (unique words) to nazwy geograficzne?"')
    print(f"\n→ {total_geo_names:,} z {unique_words:,} ({geo_percentage:.1f}%)")
    
    if geo_percentage >= 10:
        print(f"\n✅ SIGNIFICANT! Warto rozważyć specialized encoding!")
        print(f"   Hierarchical geo encoding could help!")
    elif geo_percentage >= 5:
        print(f"\n🤔 MODERATE. Może pomóc, ale nie główny cel.")
    else:
        print(f"\n➖ SMALL. Nie główny contributor do 'gap'.")
    
    print(f"\n📝 Geographic names compression strategies:")
    print(f"  1. Hierarchical: City → State → Country → Continent")
    print(f"     (e.g. 'San Francisco' → 'San' + [Francisco] + [CA] + [USA])")
    print(f"  2. Common suffixes: -burg, -ville, -ton, -ford")
    print(f"     (e.g. 'Pittsburgh' → 'Pitts' + [-burg])")
    print(f"  3. Abbreviations: 'New York' → 'NY', 'California' → 'CA'")
    print(f"  4. Geographic database: Top 1000 cities encoded specially")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    analyze_real_geographic_content("data/enwik_10mb")
    
    print("\n✨ Deep analysis complete!")
    print("🎯 Now we REALLY know how much is geography! 🗺️")
