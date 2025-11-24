#!/usr/bin/env python3
"""
ORDER-5 FAILURE ANALYSIS - What patterns does it miss?

Order-5 PPM achieves ~14.5% compression ratio.
But what specific patterns does it fail on?

If we find systematic failures, we can add specialized models! 🎯
"""
import re
from collections import Counter, defaultdict
import numpy as np

class Order5FailureAnalyzer:
    """
    Simulate Order-5 PPM and find its weaknesses
    """
    
    def __init__(self):
        self.order5_model = defaultdict(lambda: Counter())
        self.failures = []
        
    def build_order5_model(self, text, sample_size=1000000):
        """Build simplified Order-5 model"""
        print("Building Order-5 model...")
        
        # Sample for speed (full model would be huge)
        text_sample = text[:sample_size]
        
        for i in range(5, len(text_sample)):
            context = text_sample[i-5:i]
            next_char = text_sample[i]
            self.order5_model[context][next_char] += 1
        
        print(f"  Contexts: {len(self.order5_model):,}")
        print(f"  Sample size: {len(text_sample):,} chars")
        
    def test_prediction(self, text, test_size=100000):
        """
        Test Order-5 predictions and record failures
        """
        print("\nTesting Order-5 predictions...")
        
        test_text = text[:test_size]
        
        predictions = {
            'correct': 0,
            'wrong': 0,
            'no_context': 0,
        }
        
        failures = []
        
        for i in range(5, len(test_text)):
            context = test_text[i-5:i]
            actual = test_text[i]
            
            if context in self.order5_model:
                # Get top prediction
                candidates = self.order5_model[context]
                top_pred = candidates.most_common(1)[0][0] if candidates else None
                
                if top_pred == actual:
                    predictions['correct'] += 1
                else:
                    predictions['wrong'] += 1
                    
                    # Record failure
                    failures.append({
                        'context': context,
                        'expected': top_pred,
                        'actual': actual,
                        'position': i,
                        'surrounding': test_text[max(0,i-20):i+20],
                    })
            else:
                predictions['no_context'] += 1
        
        total = predictions['correct'] + predictions['wrong'] + predictions['no_context']
        
        print(f"\n  Results:")
        print(f"    Correct: {predictions['correct']:,} ({predictions['correct']/total*100:.1f}%)")
        print(f"    Wrong: {predictions['wrong']:,} ({predictions['wrong']/total*100:.1f}%)")
        print(f"    No context: {predictions['no_context']:,} ({predictions['no_context']/total*100:.1f}%)")
        
        self.failures = failures
        return predictions, failures
    
    def analyze_failure_patterns(self, failures):
        """Find common patterns in failures"""
        print("\n" + "=" * 70)
        print("🔍 ANALYZING FAILURE PATTERNS")
        print("=" * 70)
        
        # Sample failures (too many to analyze all)
        sample_failures = failures[:10000] if len(failures) > 10000 else failures
        
        print(f"\nAnalyzing {len(sample_failures):,} failure cases...")
        
        # 1. Character type failures
        print("\n1️⃣ Character Type Analysis:")
        
        char_types = {
            'lowercase': 0,
            'uppercase': 0,
            'digit': 0,
            'space': 0,
            'punctuation': 0,
            'other': 0,
        }
        
        for fail in sample_failures:
            actual = fail['actual']
            if actual.islower():
                char_types['lowercase'] += 1
            elif actual.isupper():
                char_types['uppercase'] += 1
            elif actual.isdigit():
                char_types['digit'] += 1
            elif actual == ' ':
                char_types['space'] += 1
            elif actual in '.,!?;:\'"()-':
                char_types['punctuation'] += 1
            else:
                char_types['other'] += 1
        
        total = len(sample_failures)
        for ctype, count in sorted(char_types.items(), key=lambda x: x[1], reverse=True):
            pct = count / total * 100
            print(f"  {ctype}: {count:,} ({pct:.1f}%)")
        
        # 2. Context pattern analysis
        print("\n2️⃣ Context Pattern Analysis:")
        
        context_patterns = {
            'all_lowercase': 0,
            'all_uppercase': 0,
            'mixed_case': 0,
            'has_digits': 0,
            'has_space': 0,
            'all_letters': 0,
        }
        
        for fail in sample_failures:
            context = fail['context']
            
            if context.islower():
                context_patterns['all_lowercase'] += 1
            elif context.isupper():
                context_patterns['all_uppercase'] += 1
            elif context.isalpha():
                context_patterns['mixed_case'] += 1
            
            if any(c.isdigit() for c in context):
                context_patterns['has_digits'] += 1
            if ' ' in context:
                context_patterns['has_space'] += 1
            if context.isalpha():
                context_patterns['all_letters'] += 1
        
        for pattern, count in sorted(context_patterns.items(), key=lambda x: x[1], reverse=True):
            pct = count / total * 100
            print(f"  {pattern}: {count:,} ({pct:.1f}%)")
        
        # 3. Common failure contexts
        print("\n3️⃣ Most Common Failure Contexts:")
        
        failure_contexts = Counter([f['context'] for f in sample_failures])
        
        for context, count in failure_contexts.most_common(10):
            print(f"  '{context}': {count} failures")
        
        # 4. Transition analysis
        print("\n4️⃣ Common Failed Transitions:")
        
        transitions = Counter([
            (f['expected'], f['actual']) 
            for f in sample_failures 
            if f['expected'] is not None
        ])
        
        for (expected, actual), count in transitions.most_common(10):
            print(f"  Expected '{expected}' → Got '{actual}': {count} times")
        
        # 5. Specific pattern detection
        print("\n5️⃣ Specific Pattern Failures:")
        
        patterns = {
            'xml_tags': 0,
            'templates': 0,
            'links': 0,
            'numbers': 0,
            'punctuation_switches': 0,
            'case_switches': 0,
        }
        
        for fail in sample_failures:
            surrounding = fail['surrounding']
            context = fail['context']
            actual = fail['actual']
            
            # Detect patterns
            if '<' in surrounding or '>' in surrounding:
                patterns['xml_tags'] += 1
            if '{{' in surrounding or '}}' in surrounding:
                patterns['templates'] += 1
            if '[[' in surrounding or ']]' in surrounding:
                patterns['links'] += 1
            if context[-1].isdigit() and not actual.isdigit():
                patterns['numbers'] += 1
            if context[-1] in '.,!?' and actual.isalpha():
                patterns['punctuation_switches'] += 1
            if context[-1].islower() and actual.isupper():
                patterns['case_switches'] += 1
        
        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
            pct = count / total * 100
            print(f"  {pattern}: {count:,} ({pct:.1f}%)")
        
        return {
            'char_types': char_types,
            'context_patterns': context_patterns,
            'patterns': patterns,
        }
    
    def identify_opportunities(self, failure_analysis):
        """Identify specific opportunities for improvement"""
        print("\n" + "=" * 70)
        print("💡 IMPROVEMENT OPPORTUNITIES")
        print("=" * 70)
        
        opportunities = []
        
        # 1. Case switching
        if failure_analysis['patterns']['case_switches'] > 100:
            opp = {
                'name': 'Case Switch Model',
                'failures': failure_analysis['patterns']['case_switches'],
                'description': 'Add specialized model for lowercase → uppercase transitions',
                'potential': 'Medium',
                'implementation': 'Track case patterns separately',
            }
            opportunities.append(opp)
        
        # 2. Number boundaries
        if failure_analysis['patterns']['numbers'] > 100:
            opp = {
                'name': 'Number Boundary Model',
                'failures': failure_analysis['patterns']['numbers'],
                'description': 'Predict transition from digits to non-digits',
                'potential': 'Low-Medium',
                'implementation': 'Detect number end, predict next char type',
            }
            opportunities.append(opp)
        
        # 3. Punctuation
        if failure_analysis['patterns']['punctuation_switches'] > 100:
            opp = {
                'name': 'Punctuation Model',
                'failures': failure_analysis['patterns']['punctuation_switches'],
                'description': 'Predict char after punctuation (often space/capital)',
                'potential': 'Medium',
                'implementation': 'Special model for post-punctuation chars',
            }
            opportunities.append(opp)
        
        # 4. XML/Templates
        xml_template_failures = (failure_analysis['patterns']['xml_tags'] + 
                                 failure_analysis['patterns']['templates'])
        if xml_template_failures > 100:
            opp = {
                'name': 'Structured Content Model',
                'failures': xml_template_failures,
                'description': 'Special handling for XML tags and templates',
                'potential': 'Low (already separate models?)',
                'implementation': 'Detect structured content, use grammar-based compression',
            }
            opportunities.append(opp)
        
        # 5. Uppercase failures
        if failure_analysis['char_types']['uppercase'] > 500:
            opp = {
                'name': 'Uppercase Model',
                'failures': failure_analysis['char_types']['uppercase'],
                'description': 'Predict uppercase letters (names, acronyms, titles)',
                'potential': 'Medium-High',
                'implementation': 'Case-independent model + case prediction',
            }
            opportunities.append(opp)
        
        print("\n🎯 Identified Opportunities:\n")
        
        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. {opp['name']}")
            print(f"   Failures: {opp['failures']:,}")
            print(f"   Description: {opp['description']}")
            print(f"   Potential: {opp['potential']}")
            print(f"   Implementation: {opp['implementation']}\n")
        
        # Priority ranking
        print("=" * 70)
        print("📊 PRIORITY RANKING")
        print("=" * 70)
        
        sorted_opps = sorted(opportunities, 
                           key=lambda x: x['failures'], 
                           reverse=True)
        
        print("\nBy failure count (highest priority):\n")
        for i, opp in enumerate(sorted_opps, 1):
            print(f"{i}. {opp['name']}: {opp['failures']:,} failures")
        
        return opportunities
    
    def example_failures(self, failures, n=10):
        """Show example failures for inspection"""
        print("\n" + "=" * 70)
        print(f"📝 EXAMPLE FAILURES (first {n})")
        print("=" * 70)
        
        for i, fail in enumerate(failures[:n], 1):
            print(f"\n{i}. Position {fail['position']}:")
            print(f"   Context: '{fail['context']}'")
            print(f"   Expected: '{fail['expected']}'")
            print(f"   Actual: '{fail['actual']}'")
            print(f"   Surrounding: ...{fail['surrounding']}...")

def main():
    print("=" * 70)
    print("🌙 NIGHT SESSION: ORDER-5 FAILURE ANALYSIS")
    print("=" * 70)
    print("\nWhat patterns does Order-5 PPM miss? Let's find out! 🔍\n")
    
    # Load data
    print("Loading enwik_10mb...")
    with open("data/enwik_10mb", 'rb') as f:
        data = f.read()
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Analyze
    analyzer = Order5FailureAnalyzer()
    
    # Build model
    analyzer.build_order5_model(text, sample_size=2000000)
    
    # Test and find failures
    predictions, failures = analyzer.test_prediction(text, test_size=500000)
    
    # Analyze patterns
    failure_analysis = analyzer.analyze_failure_patterns(failures)
    
    # Identify opportunities
    opportunities = analyzer.identify_opportunities(failure_analysis)
    
    # Show examples
    analyzer.example_failures(failures, n=15)
    
    print("\n" + "=" * 70)
    print("✨ Failure analysis complete!")
    print("🎯 Now we know what to improve! 🚀")
    print("=" * 70)

if __name__ == "__main__":
    main()
