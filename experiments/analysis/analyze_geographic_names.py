#!/usr/bin/env python3
"""
Analyze geographic names in Wikipedia data
Answer: Ile z "unique words" to nazwy miejsc geograficznych?

This could reveal optimization opportunity!
"""
import re
from collections import Counter

def extract_geographic_patterns(text):
    """
    Find geographic names and patterns
    """
    # Common geographic patterns
    patterns = {
        'cities_countries': [],
        'regions': [],
        'rivers_mountains': [],
        'coordinates': [],
    }
    
    # Pattern 1: Obvious geographic keywords
    geo_keywords = [
        'city', 'town', 'village', 'capital',
        'country', 'nation', 'state', 'province',
        'river', 'mountain', 'lake', 'ocean', 'sea',
        'continent', 'island', 'peninsula',
        'located in', 'situated in', 'region',
    ]
    
    # Pattern 2: Coordinates (latitude/longitude)
    coord_pattern = re.compile(r'\d+°\s*\d+[′\']\s*[NS]\s+\d+°\s*\d+[′\']\s*[EW]')
    coordinates = coord_pattern.findall(text)
    patterns['coordinates'] = coordinates
    
    # Pattern 3: Common geographic suffixes
    geo_suffixes = [
        'shire', 'land', 'ton', 'ville', 'burg', 'berg',
        'ford', 'ham', 'stead', 'port', 'mouth',
        'grad', 'ovo', 'isk', 'pol', 'stan'
    ]
    
    return patterns

def analyze_wikipedia_geography(filename):
    """Analyze geographic content in Wikipedia data"""
    
    print("=" * 70)
    print("🗺️  GEOGRAPHIC NAMES ANALYSIS")
    print("=" * 70)
    print(f"\nAnalyzing: {filename}")
    
    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    
    text = data.decode('utf-8', errors='ignore')
    
    print(f"Size: {len(data):,} bytes ({len(data)/(1024*1024):.1f} MB)\n")
    
    # Extract all words
    words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    
    print("Extracting patterns...\n")
    
    # Geographic indicators
    results = {
        'total_words': len(words),
        'unique_words': len(set(words)),
        'geographic_keywords': 0,
        'coordinate_occurrences': 0,
        'cities_explicit': 0,
        'countries_explicit': 0,
        'geographic_suffixes': 0,
        'geographic_templates': 0,
    }
    
    # Count geographic keywords
    geo_keywords = ['city', 'City', 'town', 'Town', 'village', 'Village',
                    'country', 'Country', 'nation', 'Nation',
                    'river', 'River', 'mountain', 'Mountain',
                    'located', 'situated', 'capital', 'Capital']
    
    for keyword in geo_keywords:
        results['geographic_keywords'] += text.count(keyword)
    
    # Coordinates
    coord_pattern = re.compile(r'\d+[°]\s*\d+[′\']?\s*[NS]')
    results['coordinate_occurrences'] = len(coord_pattern.findall(text))
    
    # Explicit city/country mentions
    results['cities_explicit'] = text.count('city') + text.count('City')
    results['countries_explicit'] = text.count('country') + text.count('Country')
    
    # Geographic templates (Wikipedia specific)
    geo_templates = [
        '{{coord', '{{Coord', '{{location', '{{Location',
        '{{Infobox settlement', '{{Infobox country',
        '{{Geobox'
    ]
    
    for template in geo_templates:
        results['geographic_templates'] += text.count(template)
    
    # Geographic suffixes in proper nouns
    geo_suffixes = ['shire', 'land', 'ton', 'ville', 'burg', 'berg',
                    'ford', 'ham', 'stead', 'port', 'mouth',
                    'grad', 'ovo', 'isk', 'pol', 'stan']
    
    capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', text)
    
    for word in capitalized_words:
        for suffix in geo_suffixes:
            if word.lower().endswith(suffix):
                results['geographic_suffixes'] += 1
                break
    
    # Print results
    print("=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    
    print(f"\nTotal capitalized words: {results['total_words']:,}")
    print(f"Unique capitalized words: {results['unique_words']:,}")
    
    print(f"\n🗺️  Geographic indicators:")
    print(f"  Keywords (city, country, river...): {results['geographic_keywords']:,}")
    print(f"  Coordinates (lat/long): {results['coordinate_occurrences']:,}")
    print(f"  'city' mentions: {results['cities_explicit']:,}")
    print(f"  'country' mentions: {results['countries_explicit']:,}")
    print(f"  Geographic templates: {results['geographic_templates']:,}")
    print(f"  Words with geo suffixes: {results['geographic_suffixes']:,}")
    
    # Estimate percentage
    print(f"\n📊 Estimation:")
    
    # Very rough estimate
    total_geo_indicators = (results['geographic_keywords'] + 
                           results['coordinate_occurrences'] + 
                           results['geographic_suffixes'])
    
    # Each article might have 5-10 geographic names
    estimated_geo_articles = results['geographic_templates'] * 8
    
    print(f"  Estimated geographic articles: ~{estimated_geo_articles:,}")
    print(f"  Geographic indicators total: {total_geo_indicators:,}")
    
    # More sophisticated analysis
    print(f"\n🎯 Detailed breakdown:")
    
    # Find actual place names (heuristic)
    # Look for patterns like "X is a city in Y"
    city_pattern = re.compile(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+is\s+a\s+city')
    cities_found = city_pattern.findall(text)
    
    country_pattern = re.compile(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+is\s+a\s+country')
    countries_found = country_pattern.findall(text)
    
    print(f"  Explicit city definitions: {len(cities_found)}")
    print(f"  Explicit country definitions: {len(countries_found)}")
    
    if cities_found:
        print(f"\n  Sample cities: {', '.join(cities_found[:10])}")
    
    if countries_found:
        print(f"  Sample countries: {', '.join(countries_found[:10])}")
    
    # Estimate percentage of total unique words
    estimated_geo_names = len(set(cities_found + countries_found)) * 3  # Multiply for other types
    geo_percentage = (estimated_geo_names / results['unique_words']) * 100 if results['unique_words'] > 0 else 0
    
    print(f"\n💡 Conservative estimate:")
    print(f"  Unique geographic names: ~{estimated_geo_names:,}")
    print(f"  As % of unique words: ~{geo_percentage:.1f}%")
    
    # Compression impact
    print(f"\n🎯 COMPRESSION IMPACT:")
    
    avg_geo_name_length = 12  # "Buenos Aires", "San Francisco", etc.
    total_geo_bytes = estimated_geo_names * avg_geo_name_length
    
    print(f"  Estimated bytes in geo names: ~{total_geo_bytes:,} bytes")
    print(f"  As % of total: ~{(total_geo_bytes/len(data))*100:.2f}%")
    
    # If we could compress geo names 50% better
    potential_saving = total_geo_bytes * 0.5
    print(f"\n  If 50% better compression of geo names:")
    print(f"    Potential saving: ~{potential_saving:,} bytes = {potential_saving/1024:.0f} KB")
    
    print(f"\n" + "=" * 70)
    print("💭 INTERPRETATION")
    print("=" * 70)
    
    if geo_percentage > 5:
        print(f"\n✅ Geographic names are SIGNIFICANT ({geo_percentage:.1f}%)!")
        print(f"   Worth exploring specialized encoding!")
    elif geo_percentage > 2:
        print(f"\n🤔 Geographic names are MODERATE ({geo_percentage:.1f}%)")
        print(f"   Could help, but not primary target")
    else:
        print(f"\n➖ Geographic names are SMALL ({geo_percentage:.1f}%)")
        print(f"   Probably not the main 'gap'")
    
    print(f"\n📝 Geographic compression strategies:")
    print(f"  1. Coordinate compression (lat/long patterns)")
    print(f"  2. Hierarchical encoding (City → Country → Continent)")
    print(f"  3. Common suffixes (-burg, -ville, -stan)")
    print(f"  4. Geographic relationships (nearby cities)")
    
    return results

if __name__ == "__main__":
    print("🚀 Starting geographic analysis...\n")
    
    # Analyze 10 MB file
    results = analyze_wikipedia_geography("data/enwik_10mb")
    
    print("\n✨ Analysis complete!")
    print("🎯 Now we know how much of 'gap' is geography! 🗺️")
