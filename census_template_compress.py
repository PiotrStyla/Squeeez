#!/usr/bin/env python3
"""
Census Template Compression for enwik9
Detects US city/town articles with census data and compresses them to binary format.
"""
import re
import struct
from collections import defaultdict

# US States mapping (2-letter codes)
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
ID_TO_STATE = {i: v for v, i in STATE_TO_ID.items()}

# Patterns for census data
CENSUS_PATTERNS = {
    'population': r'there were (\d[\d,]*) people',
    'households': r'(\d[\d,]*) households',
    'families': r'(\d[\d,]*) families',
    'density_pop': r'population density (?:was |of )?(\d[\d,\.]*)',
    'density_housing': r'housing density (?:was |of )?(\d[\d,\.]*)',
    'median_income_household': r'median income for a household[^$]*\$(\d[\d,]*)',
    'median_income_family': r'median income for a family[^$]*\$(\d[\d,]*)',
    'per_capita': r'per capita income[^$]*\$(\d[\d,]*)',
    'males': r'(\d[\d,]*) males',
    'females': r'(\d[\d,]*) females',
    'land_area': r'land area of (\d[\d,\.]*)',
    'water_area': r'water area of (\d[\d,\.]*)',
    'elevation': r'elevation[^\d]*(\d[\d,]*)',
    'zip_code': r'ZIP code[^\d]*(\d{5})',
    'area_code': r'area code[^\d]*(\d{3})',
}

# Age distribution patterns
AGE_PATTERNS = [
    (r'under the age of 18', 'under_18'),
    (r'from 18 to 24', 'age_18_24'),
    (r'from 25 to 44', 'age_25_44'),
    (r'from 45 to 64', 'age_45_64'),
    (r'65 years of age or older', 'age_65_plus'),
]

def parse_number(s):
    """Convert string number with commas to int"""
    if not s:
        return 0
    return int(s.replace(',', '').replace('.', ''))

def parse_float(s):
    """Convert string to float"""
    if not s:
        return 0.0
    return float(s.replace(',', ''))

def detect_census_article(title, text):
    """Check if article is a US census-style location article"""
    # Check for state name in title or text
    for state_name in US_STATES:
        if state_name in title or f', {US_STATES[state_name]}' in title:
            # Check for census keywords
            if 'census' in text.lower() and 'population' in text.lower():
                return True, state_name
    return False, None

def extract_census_data(text):
    """Extract structured census data from article text"""
    data = {}
    
    # Extract numeric data
    for key, pattern in CENSUS_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                if 'density' in key or 'area' in key:
                    data[key] = parse_float(match.group(1))
                else:
                    data[key] = parse_number(match.group(1))
            except:
                pass
    
    # Extract percentages for age distribution
    for pattern, key in AGE_PATTERNS:
        match = re.search(pattern + r'[^%]*?(\d+\.?\d*)%', text, re.IGNORECASE)
        if match:
            try:
                data[key] = float(match.group(1))
            except:
                pass
    
    return data

def encode_census_binary(title, state, data):
    """Encode census data to compact binary format"""
    # Format: [MARKER][title_len][title][state_id][field_count][fields...]
    # Each field: [field_id:1byte][value:4bytes]
    
    FIELD_IDS = {
        'population': 1, 'households': 2, 'families': 3,
        'median_income_household': 4, 'median_income_family': 5, 'per_capita': 6,
        'males': 7, 'females': 8, 'zip_code': 9, 'area_code': 10,
        'under_18': 11, 'age_18_24': 12, 'age_25_44': 13, 'age_45_64': 14, 'age_65_plus': 15,
    }
    
    # Encode title
    title_bytes = title.encode('utf-8')[:255]
    
    # State ID
    state_code = US_STATES.get(state, 'XX')
    state_id = STATE_TO_ID.get(state_code, 99)
    
    # Build binary
    result = bytearray()
    result.append(0xCE)  # Census marker
    result.append(len(title_bytes))
    result.extend(title_bytes)
    result.append(state_id)
    
    # Encode fields
    fields = []
    for key, value in data.items():
        if key in FIELD_IDS and value:
            field_id = FIELD_IDS[key]
            if isinstance(value, float):
                # Encode percentage as fixed point (x100)
                int_val = int(value * 100)
            else:
                int_val = min(value, 0xFFFFFFFF)
            fields.append((field_id, int_val))
    
    result.append(len(fields))
    for field_id, value in fields:
        result.append(field_id)
        result.extend(struct.pack('<I', value))
    
    return bytes(result)

def decode_census_binary(data):
    """Decode binary census data back to text (for verification)"""
    if data[0] != 0xCE:
        return None
    
    pos = 1
    title_len = data[pos]
    pos += 1
    title = data[pos:pos+title_len].decode('utf-8')
    pos += title_len
    state_id = data[pos]
    pos += 1
    field_count = data[pos]
    pos += 1
    
    fields = {}
    FIELD_NAMES = {
        1: 'population', 2: 'households', 3: 'families',
        4: 'median_income_household', 5: 'median_income_family', 6: 'per_capita',
        7: 'males', 8: 'females', 9: 'zip_code', 10: 'area_code',
        11: 'under_18', 12: 'age_18_24', 13: 'age_25_44', 14: 'age_45_64', 15: 'age_65_plus',
    }
    
    for _ in range(field_count):
        field_id = data[pos]
        pos += 1
        value = struct.unpack('<I', data[pos:pos+4])[0]
        pos += 4
        if field_id in FIELD_NAMES:
            fields[FIELD_NAMES[field_id]] = value
    
    return {'title': title, 'state': ID_TO_STATE.get(state_id, '??'), 'fields': fields}

def process_enwik9(input_path, output_path):
    """Process enwik9 and compress census articles"""
    print(f"Loading {input_path}...")
    with open(input_path, 'r', errors='ignore') as f:
        data = f.read()
    
    print(f"Loaded {len(data):,} bytes")
    
    # Find articles
    article_pattern = re.compile(r'<title>(.*?)</title>.*?<text[^>]*>(.*?)</text>', re.DOTALL)
    
    census_articles = []
    non_census_parts = []
    last_end = 0
    
    total_original_size = 0
    total_compressed_size = 0
    
    print("Scanning for census articles...")
    for match in article_pattern.finditer(data):
        title = match.group(1)
        text = match.group(2)
        
        is_census, state = detect_census_article(title, text)
        
        if is_census:
            census_data = extract_census_data(text)
            if len(census_data) >= 3:  # At least 3 fields extracted
                # Save non-census part before this article
                non_census_parts.append(data[last_end:match.start()])
                
                # Compress census article
                binary = encode_census_binary(title, state, census_data)
                census_articles.append({
                    'title': title,
                    'original_size': len(match.group(0)),
                    'compressed_size': len(binary),
                    'binary': binary,
                    'data': census_data,
                })
                
                total_original_size += len(match.group(0))
                total_compressed_size += len(binary)
                
                last_end = match.end()
                
                if len(census_articles) % 1000 == 0:
                    print(f"  Found {len(census_articles)} census articles...")
    
    # Add remaining content
    non_census_parts.append(data[last_end:])
    
    print(f"\n=== RESULTS ===")
    print(f"Census articles found: {len(census_articles)}")
    print(f"Original size (census): {total_original_size:,} bytes ({total_original_size/1024/1024:.2f} MB)")
    print(f"Compressed size: {total_compressed_size:,} bytes ({total_compressed_size/1024/1024:.2f} MB)")
    print(f"Savings: {total_original_size - total_compressed_size:,} bytes ({(total_original_size - total_compressed_size)/1024/1024:.2f} MB)")
    print(f"Compression ratio: {total_compressed_size/total_original_size*100:.1f}%")
    
    # Sample output
    print(f"\nSample compressed articles:")
    for art in census_articles[:5]:
        print(f"  {art['title'][:50]}: {art['original_size']} -> {art['compressed_size']} bytes")
        print(f"    Data: {art['data']}")
    
    # Write output
    if output_path:
        print(f"\nWriting to {output_path}...")
        with open(output_path, 'wb') as f:
            # Header
            f.write(b'CENSUS_COMPRESSED_V1\n')
            f.write(struct.pack('<I', len(census_articles)))
            
            # Census articles binary blob
            for art in census_articles:
                f.write(struct.pack('<H', len(art['binary'])))
                f.write(art['binary'])
            
            # Non-census content (as-is)
            f.write(b'\n---NON_CENSUS_START---\n')
            for part in non_census_parts:
                f.write(part.encode('utf-8', errors='ignore'))
        
        import os
        final_size = os.path.getsize(output_path)
        original_size = len(data)
        print(f"\nFinal file size: {final_size:,} bytes ({final_size/1024/1024:.2f} MB)")
        print(f"Original size: {original_size:,} bytes ({original_size/1024/1024:.2f} MB)")
        print(f"Total savings: {original_size - final_size:,} bytes ({(original_size - final_size)/1024/1024:.2f} MB)")

if __name__ == '__main__':
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else '/root/hutter/paq8px/enwik9_reordered_transformed'
    output_file = sys.argv[2] if len(sys.argv) > 2 else '/root/hutter/paq8px/enwik9_census_compressed'
    process_enwik9(input_file, output_file)
