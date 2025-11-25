#!/usr/bin/env python3
"""
PATTERN DISCOVERY ENGINE - What does Order-5 miss?

Find SPECIFIC patterns where Order-5 fails.
These are opportunities for specialized models! 🎯

Approach:
1. Build Order-5 model
2. Find where it predicts wrong
3. Categorize failure patterns
4. Identify systematic weaknesses
5. Suggest targeted improvements!
"""
import re
from collections import defaultdict, Counter
import numpy as np

class PatternDiscoveryEngine:
    """
    Discover patterns where Order-5 compression fails
    """
    
    def __init__(self):
        self.order5_model = defaultdict(lambda: Counter())
        self.failures = []
        
    def build_order5(self, text, sample_size=1000000):
        """Build Order-5 model"""
        print("=" * 70)
        print("🔨 BUILDING ORDER-5 MODEL")
        print("=" * 70)
        
        sample = text[:sample_size]
        
        for i in range(5, len(sample)):
            context = sample[i-5:i]
            next_char = sample[i]
            self.order5_model[context][next_char] += 1
        
        print(f"\nContexts learned: {len(self.order5_model):,}")
        print(f"Sample size: {len(sample):,} chars\n")
    
    def find_failures(self, text, test_size=200000):
        """Find where Order-5 predicts incorrectly"""
        print("=" * 70)
        print("🔍 FINDING FAILURE PATTERNS")
        print("=" * 70)
        
        # Use fresh test data
        test_start = 1000000
        test_text = text[test_start:test_start + test_size]
        
        print(f"\nTesting on {len(test_text):,} fresh chars...")
        
        failures = []
        correct = 0
        wrong = 0
        
        for i in range(5, len(test_text)):
            context = test_text[i-5:i]
            actual = test_text[i]
            
            if context in self.order5_model:
                predictions = self.order5_model[context]
                top_pred = predictions.most_common(1)[0][0]
                
                if top_pred == actual:
                    correct += 1
                else:
                    wrong += 1
                    # Record failure
                    failures.append({
                        'context': context,
                        'predicted': top_pred,
                        'actual': actual,
                        'position': i + test_start,
                        'window': test_text[max(0,i-20):min(len(test_text),i+20)],
                    })
            else:
                wrong += 1  # No context = failure
                failures.append({
                    'context': context,
                    'predicted': None,
                    'actual': actual,
                    'position': i + test_start,
                    'window': test_text[max(0,i-20):min(len(test_text),i+20)],
                })
        
        total = correct + wrong
        print(f"\nResults:")
        print(f"  Correct: {correct:,} ({correct/total*100:.1f}%)")
        print(f"  Wrong: {wrong:,} ({wrong/total*100:.1f}%)")
        print(f"  Failure rate: {wrong/total*100:.1f}%")
        
        self.failures = failures
        return failures
    
    def categorize_failures(self, failures):
        """Categorize failures by pattern type"""
        print("\n" + "=" * 70)
        print("📊 CATEGORIZING FAILURE PATTERNS")
        print("=" * 70)
        
        # Sample for analysis
        sample = failures[:10000] if len(failures) > 10000 else failures
        
        categories = {
            # Structural patterns
            'xml_tag': 0,
            'template': 0,
            'link': 0,
            
            # Character transitions
            'case_switch': 0,
            'number_boundary': 0,
            'punctuation_after': 0,
            'space_after_punctuation': 0,
            
            # Character types
            'uppercase_fail': 0,
            'lowercase_fail': 0,
            'digit_fail': 0,
            'symbol_fail': 0,
            
            # Specific patterns
            'year_pattern': 0,
            'url_pattern': 0,
            'acronym': 0,
            'title_case': 0,
            
            # Context patterns
            'rare_context': 0,
            'ambiguous_context': 0,
        }
        
        examples = defaultdict(list)
        
        for fail in sample:
            context = fail['context']
            actual = fail['actual']
            predicted = fail['predicted']
            window = fail['window']
            
            # Structural
            if '<' in window or '>' in window:
                categories['xml_tag'] += 1
                if len(examples['xml_tag']) < 3:
                    examples['xml_tag'].append((context, predicted, actual, window))
            
            if '{{' in window or '}}' in window:
                categories['template'] += 1
                if len(examples['template']) < 3:
                    examples['template'].append((context, predicted, actual, window))
            
            if '[[' in window or ']]' in window:
                categories['link'] += 1
                if len(examples['link']) < 3:
                    examples['link'].append((context, predicted, actual, window))
            
            # Transitions
            if context[-1].islower() and actual.isupper():
                categories['case_switch'] += 1
                if len(examples['case_switch']) < 3:
                    examples['case_switch'].append((context, predicted, actual, window))
            
            if context[-1].isdigit() and not actual.isdigit():
                categories['number_boundary'] += 1
                if len(examples['number_boundary']) < 3:
                    examples['number_boundary'].append((context, predicted, actual, window))
            
            if context[-1] in '.!?,;:' and actual != ' ':
                categories['punctuation_after'] += 1
                if len(examples['punctuation_after']) < 3:
                    examples['punctuation_after'].append((context, predicted, actual, window))
            
            if context[-1] in '.!?' and actual == ' ':
                categories['space_after_punctuation'] += 1
            
            # Character types
            if actual.isupper():
                categories['uppercase_fail'] += 1
            elif actual.islower():
                categories['lowercase_fail'] += 1
            elif actual.isdigit():
                categories['digit_fail'] += 1
            else:
                categories['symbol_fail'] += 1
            
            # Specific patterns
            if context.isdigit() and len(context) >= 4:
                categories['year_pattern'] += 1
                if len(examples['year_pattern']) < 3:
                    examples['year_pattern'].append((context, predicted, actual, window))
            
            if 'http' in window.lower() or 'www' in window.lower():
                categories['url_pattern'] += 1
            
            if context.isupper() and len(context) >= 3:
                categories['acronym'] += 1
                if len(examples['acronym']) < 3:
                    examples['acronym'].append((context, predicted, actual, window))
            
            # Context
            if predicted is None:
                categories['rare_context'] += 1
        
        # Results
        print(f"\nAnalyzed {len(sample):,} failures\n")
        
        print("TOP FAILURE CATEGORIES:\n")
        
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        for cat, count in sorted_cats[:15]:
            if count > 0:
                pct = count / len(sample) * 100
                print(f"  {cat:.<30} {count:>6,} ({pct:>5.1f}%)")
        
        return categories, examples
    
    def identify_opportunities(self, categories, examples):
        """Identify specific improvement opportunities"""
        print("\n" + "=" * 70)
        print("💡 IMPROVEMENT OPPORTUNITIES")
        print("=" * 70)
        
        opportunities = []
        
        # Analyze each category
        total_failures = sum(categories.values())
        
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            if count < 100:  # Skip rare patterns
                continue
            
            pct = count / total_failures * 100
            
            opportunity = {
                'pattern': cat,
                'failures': count,
                'percent': pct,
                'examples': examples.get(cat, [])[:3],
            }
            
            # Add recommendations
            if cat == 'case_switch':
                opportunity['solution'] = 'Case-aware model: Track case transitions separately'
                opportunity['potential'] = 'Medium-High'
                opportunity['complexity'] = 'Low'
            
            elif cat == 'number_boundary':
                opportunity['solution'] = 'Number boundary model: Detect end of numbers'
                opportunity['potential'] = 'Medium'
                opportunity['complexity'] = 'Low'
            
            elif cat == 'punctuation_after':
                opportunity['solution'] = 'Post-punctuation model: Special handling after .,!?'
                opportunity['potential'] = 'Medium-High'
                opportunity['complexity'] = 'Low'
            
            elif cat == 'xml_tag':
                opportunity['solution'] = 'XML structure model: Grammar-based encoding'
                opportunity['potential'] = 'Medium'
                opportunity['complexity'] = 'Medium'
            
            elif cat == 'uppercase_fail':
                opportunity['solution'] = 'Uppercase model: Predict uppercase letters separately'
                opportunity['potential'] = 'High'
                opportunity['complexity'] = 'Medium'
            
            elif cat == 'rare_context':
                opportunity['solution'] = 'Better fallback: Improve rare context handling'
                opportunity['potential'] = 'Medium'
                opportunity['complexity'] = 'Medium'
            
            elif cat == 'acronym':
                opportunity['solution'] = 'Acronym detector: Special model for all-caps sequences'
                opportunity['potential'] = 'Low-Medium'
                opportunity['complexity'] = 'Low'
            
            else:
                opportunity['solution'] = 'Pattern-specific model needed'
                opportunity['potential'] = 'Unknown'
                opportunity['complexity'] = 'Unknown'
            
            opportunities.append(opportunity)
        
        # Display
        print("\nTOP OPPORTUNITIES (sorted by impact):\n")
        
        for i, opp in enumerate(opportunities[:10], 1):
            print(f"{i}. {opp['pattern'].upper().replace('_', ' ')}")
            print(f"   Failures: {opp['failures']:,} ({opp['percent']:.1f}%)")
            print(f"   Solution: {opp['solution']}")
            print(f"   Potential: {opp['potential']}")
            print(f"   Complexity: {opp['complexity']}")
            
            if opp['examples']:
                print(f"   Examples:")
                for ctx, pred, act, win in opp['examples'][:2]:
                    pred_str = f"'{pred}'" if pred else "None"
                    print(f"     Context: '{ctx}' → Predicted: {pred_str}, Actual: '{act}'")
            
            print()
        
        return opportunities
    
    def estimate_impact(self, opportunities):
        """Estimate compression impact of fixing these patterns"""
        print("=" * 70)
        print("📈 IMPACT ESTIMATION")
        print("=" * 70)
        
        total_failures = sum(opp['failures'] for opp in opportunities)
        
        # Assume fixing a pattern reduces its bits by 50%
        # (better prediction = fewer bits needed)
        
        print(f"\nTotal failures analyzed: {total_failures:,}")
        print("\nIf we fix TOP opportunities:\n")
        
        cumulative_impact = 0
        
        for i, opp in enumerate(opportunities[:5], 1):
            # Estimate: Each failure costs ~3 extra bits on average
            # (wrong prediction → more bits needed)
            failure_cost = opp['failures'] * 3
            
            # Fixing reduces by 50%
            potential_savings = failure_cost * 0.5
            cumulative_impact += potential_savings
            
            print(f"{i}. {opp['pattern']}")
            print(f"   Failures: {opp['failures']:,}")
            print(f"   Potential bits saved: {potential_savings:,.0f}")
            print(f"   Estimated KB saved: {potential_savings / 8 / 1024:.2f}")
        
        print(f"\n🎯 CUMULATIVE IMPACT (Top 5):")
        print(f"   Total bits saved: {cumulative_impact:,.0f}")
        print(f"   Total KB saved: {cumulative_impact / 8 / 1024:.2f}")
        
        # Extrapolate to full enwik9
        scale = 1000  # 1GB / 1MB
        full_impact = cumulative_impact / 8 / 1024 * scale
        
        print(f"\n🌍 EXTRAPOLATED TO ENWIK9 (1 GB):")
        print(f"   Potential MB saved: {full_impact / 1024:.2f}")
        
        if full_impact / 1024 > 5:
            print(f"\n   🏆 SIGNIFICANT! Worth pursuing!")
        elif full_impact / 1024 > 1:
            print(f"\n   🎯 Solid potential! Consider it!")
        else:
            print(f"\n   ➖ Modest impact.")
        
        return cumulative_impact

def main():
    print("=" * 70)
    print("🔬 PATTERN DISCOVERY ENGINE")
    print("=" * 70)
    print("\nFinding what Order-5 misses → Targeted improvements! 🎯\n")
    
    # Load data
    print("Loading enwik_10mb...")
    with open("data/enwik_10mb", 'rb') as f:
        data = f.read()
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Initialize engine
    engine = PatternDiscoveryEngine()
    
    # Build Order-5 model
    engine.build_order5(text, sample_size=1000000)
    
    # Find failures
    failures = engine.find_failures(text, test_size=200000)
    
    # Categorize
    categories, examples = engine.categorize_failures(failures)
    
    # Identify opportunities
    opportunities = engine.identify_opportunities(categories, examples)
    
    # Estimate impact
    engine.estimate_impact(opportunities)
    
    print("\n" + "=" * 70)
    print("✨ Pattern discovery complete!")
    print("🎯 Now we know WHAT to fix! 🚀")
    print("=" * 70)

if __name__ == "__main__":
    main()
