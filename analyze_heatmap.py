#!/usr/bin/env python3
"""
Heat Map + Temperature Analysis for enwik9
Analyzes word frequencies, article entropy, and clustering potential
"""
import re
import math
from collections import Counter, defaultdict

def calculate_entropy(text):
    """Calculate Shannon entropy of text"""
    if not text:
        return 0
    freq = Counter(text)
    length = len(text)
    return -sum((c/length) * math.log2(c/length) for c in freq.values() if c > 0)

def word_frequency(data, top_n=200):
    """Get word frequency heat map"""
    words = re.findall(r'[a-zA-Z]{3,}', data[:100000000])
    return Counter(words).most_common(top_n)

def analyze_patterns(data):
    """Find most common Wikipedia patterns"""
    patterns = {
        'Category links': r'\[\[Category:[^\]]+\]\]',
        'Internal links': r'\[\[[^\]]+\]\]',
        'Templates': r'\{\{[^}]+\}\}',
        'H2 headers': r'== [^=]+ ==',
        'H3 headers': r'=== [^=]+ ===',
        'References': r'<ref[^>]*>.*?</ref>',
        'External URLs': r'https?://[^\s\]]+',
    }
    
    results = {}
    sample = data[:50000000]  # First 50MB for speed
    for name, pattern in patterns.items():
        matches = re.findall(pattern, sample, re.DOTALL)
        results[name] = len(matches)
    return results

def find_repeated_phrases(data, min_len=15, max_len=50, sample_size=30000000):
    """Find repeated phrases for dictionary compression"""
    sample = data[:sample_size]
    phrases = defaultdict(int)
    
    # Sample every 50 chars to find repeated phrases
    for phrase_len in [15, 20, 25, 30]:
        for i in range(0, len(sample) - phrase_len, 50):
            phrase = sample[i:i+phrase_len]
            if phrase.isprintable() and not phrase.isspace():
                phrases[phrase] += 1
    
    # Filter to phrases that appear 50+ times
    repeated = [(p, c) for p, c in phrases.items() if c >= 50]
    # Sort by potential savings (count * length)
    repeated.sort(key=lambda x: -x[1] * len(x[0]))
    return repeated[:100]

def analyze_articles(data, max_articles=1000):
    """Analyze articles for temperature/clustering"""
    pattern = re.compile(r'<title>(.*?)</title>.*?<text[^>]*>(.*?)</text>', re.DOTALL)
    
    articles = []
    for i, match in enumerate(pattern.finditer(data[:200000000])):
        if i >= max_articles:
            break
        title = match.group(1)
        text = match.group(2)[:10000]  # First 10KB of article
        
        entropy = calculate_entropy(text)
        link_count = text.count('[[')
        template_count = text.count('{{')
        text_len = len(text)
        
        # Temperature classification
        if link_count > 100 or template_count > 50:
            temp = 'HOT'
        elif link_count > 30 or template_count > 15:
            temp = 'WARM'
        else:
            temp = 'COLD'
        
        articles.append({
            'title': title[:50],
            'entropy': entropy,
            'links': link_count,
            'templates': template_count,
            'length': text_len,
            'temperature': temp
        })
    
    return articles

def main():
    print("=" * 60)
    print("HEAT MAP + TEMPERATURE ANALYSIS FOR ENWIK9")
    print("=" * 60)
    
    print("\nLoading enwik9_reordered_transformed...")
    with open('/root/hutter/paq8px/enwik9_reordered_transformed', 'r', errors='ignore') as f:
        data = f.read()
    
    print(f"Loaded {len(data):,} bytes ({len(data)/1024/1024:.1f} MB)")
    
    # 1. Word frequency heat map
    print("\n" + "=" * 60)
    print("WORD FREQUENCY HEAT MAP (Top 50)")
    print("=" * 60)
    words = word_frequency(data, 50)
    total_words = sum(c for _, c in words)
    for i, (word, count) in enumerate(words, 1):
        pct = count / total_words * 100
        bar = '#' * min(40, int(pct * 4))
        print(f"{i:3}. {word:20} {count:>10,} ({pct:5.2f}%) {bar}")
    
    # 2. Pattern frequency
    print("\n" + "=" * 60)
    print("WIKIPEDIA PATTERN FREQUENCY")
    print("=" * 60)
    patterns = analyze_patterns(data)
    for name, count in sorted(patterns.items(), key=lambda x: -x[1]):
        print(f"{count:>12,} : {name}")
    
    # 3. Repeated phrases (compression opportunities)
    print("\n" + "=" * 60)
    print("REPEATED PHRASES (Dictionary Compression Opportunities)")
    print("=" * 60)
    phrases = find_repeated_phrases(data)
    print(f"Found {len(phrases)} highly repeated phrases")
    print("\nTop 30 by potential savings:")
    total_savings = 0
    for phrase, count in phrases[:30]:
        savings = count * (len(phrase) - 2)
        total_savings += savings
        phrase_display = phrase.replace('\n', '\\n')[:40]
        print(f"  {count:>6}x [{len(phrase):2}ch] '{phrase_display:40}' -> save {savings:>10,} bytes")
    
    print(f"\nTotal potential savings from top 30 phrases: {total_savings:,} bytes ({total_savings/1024/1024:.2f} MB)")
    
    # 4. Article temperature analysis
    print("\n" + "=" * 60)
    print("ARTICLE TEMPERATURE ANALYSIS")
    print("=" * 60)
    articles = analyze_articles(data, 500)
    
    temps = Counter(a['temperature'] for a in articles)
    print(f"\nTemperature distribution (sample of {len(articles)} articles):")
    for temp, count in temps.most_common():
        pct = count / len(articles) * 100
        bar = '#' * int(pct / 2)
        print(f"  {temp:4}: {count:4} ({pct:5.1f}%) {bar}")
    
    print("\nSample HOT articles (high link/template density):")
    hot = [a for a in articles if a['temperature'] == 'HOT'][:10]
    for a in hot:
        print(f"  Links:{a['links']:3} Templ:{a['templates']:3} Entropy:{a['entropy']:.2f} | {a['title']}")
    
    print("\nSample COLD articles (low link/template density):")
    cold = [a for a in articles if a['temperature'] == 'COLD'][:10]
    for a in cold:
        print(f"  Links:{a['links']:3} Templ:{a['templates']:3} Entropy:{a['entropy']:.2f} | {a['title']}")
    
    # 5. Entropy distribution
    print("\n" + "=" * 60)
    print("ENTROPY DISTRIBUTION")
    print("=" * 60)
    entropies = [a['entropy'] for a in articles]
    avg_entropy = sum(entropies) / len(entropies)
    min_entropy = min(entropies)
    max_entropy = max(entropies)
    print(f"Average entropy: {avg_entropy:.3f}")
    print(f"Min entropy: {min_entropy:.3f}")
    print(f"Max entropy: {max_entropy:.3f}")
    
    # Histogram
    buckets = [0] * 10
    for e in entropies:
        bucket = min(9, int((e - 3) / 0.5))
        if bucket >= 0:
            buckets[bucket] += 1
    
    print("\nEntropy histogram:")
    for i, count in enumerate(buckets):
        low = 3 + i * 0.5
        high = low + 0.5
        bar = '#' * (count // 2)
        print(f"  {low:.1f}-{high:.1f}: {count:4} {bar}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print("\nRecommendations for compression:")
    print("1. Build dictionary from top 1000 repeated phrases")
    print("2. Group articles by temperature for better context modeling")
    print("3. Separate high-entropy from low-entropy content")
    print("4. Extract and compress templates/markup separately")

if __name__ == '__main__':
    main()
