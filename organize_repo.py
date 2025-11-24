#!/usr/bin/env python3
"""
Repository Organization Script

Clean up HutterLab repository for public consumption
"""
import os
import shutil
from pathlib import Path

def organize_repository():
    """Organize repository into clear structure"""
    
    print("=" * 70)
    print("📁 ORGANIZING REPOSITORY")
    print("=" * 70)
    
    base = Path("C:/HutterLab")
    
    # Define organization structure
    organization = {
        # KEEP these important MD files (move to docs/)
        'docs/': [
            'README.md',  # Main README stays in root, but copy to docs
            'TODAY_COMPLETE_SUMMARY.md',
            'WORLD_RECORD_ROADMAP.md',
        ],
        
        # Archive old session summaries
        'archive/sessions/': [
            'ANALYSIS.md',
            'BREAKTHROUGH.md', 
            'CELEBRATION.md',
            'DISCOVERY_PATH.md',
            'EPIC_JOURNEY.md',
            'FINAL_SESSION_REPORT.md',
            'GRAND_SUMMARY.md',
            'MOMENTUM.md',
            'NEXT_SESSION.md',
            'SESSION_FINAL.md',
            'SESSION_SUMMARY.md',
            'STATUS.md',
            'SUMMARY.md',
            'THE_STORY.md',
        ],
        
        # Move experimental analysis scripts
        'experiments/analysis/': [
            'analyze_chemical_compounds.py',
            'analyze_entities.py',
            'analyze_enwik.py',
            'analyze_enwik_simple.py',
            'analyze_geographic_names.py',
            'analyze_link_relations.py',
            'analyze_sections.py',
            'analyze_templates.py',
            'analyze_type_prediction.py',
            'geographic_deep_analysis.py',
            'graph_analysis.py',
            'semantic_boost_analysis.py',
        ],
        
        # Move test scripts
        'experiments/tests/': [
            'test_10mb_full.py',
            'test_enwik.py',
            'test_extreme_orders.py',
            'test_higher_order.py',
            'test_multichannel_1mb.py',
            'test_multichannel_small.py',
            'test_order5_1mb.py',
            'test_order6_10mb.py',
            'test_order6_1mb.py',
            'test_order7_1mb.py',
            'test_probabilistic_real.py',
            'test_ultimate_10mb.py',
            'test_ultra_100mb.py',
            'test_ultra_10mb.py',
        ],
        
        # Move exploratory compressors
        'experiments/exploratory/': [
            'adaptive_order_analysis.py',
            'adaptive_ultra_compressor.py',
            'bayesian_compressor.py',
            'compress_arithmetic.py',
            'compress_context.py',
            'compress_demo.py',
            'full_structure_compressor.py',
            'graph_compressor.py',
            'graph_template_compressor.py',
            'hybrid_compressor.py',
            'multichannel_compressor.py',
            'multirel_compressor.py',
            'ultra_compressor.py',
            'ultra_final_optimal.py',
            'ultra_maximum_squeeze.py',
            'ultra_microopt.py',
            'ultra_optimized.py',
            'ultra_trigram.py',
        ],
        
        # Move ZKP research
        'experiments/zkp_research/': [
            'probabilistic_zkp.py',
            'zkp_link_test.py',
            'zkp_link_test_v2.py',
            'neural_properties.py',
        ],
        
        # Archive duplicate/old READMEs
        'archive/old_docs/': [
            'README_FINAL.md',
            'README_NEW.md',
            'README_PL.md',
            'ROADMAP_INNOVATION.md',
            'TROUBLESHOOTING.md',
        ],
        
        # Archive results files
        'archive/results/': [
            'ENWIK8_RESULTS.txt',
            'FINAL_OPTIMAL_RESULTS.txt',
            'ORDER6_10MB_RESULTS.txt',
            'ORDER7_RESULTS.txt',
            'ULTRA_OPTIMIZED_RESULTS.txt',
            'ULTRA_RESULTS.txt',
        ],
    }
    
    # Create directories
    print("\n1️⃣ Creating directory structure...")
    for dir_path in organization.keys():
        full_path = base / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"   Created: {dir_path}")
    
    # Move files
    print("\n2️⃣ Moving files...")
    moved_count = 0
    for dest_dir, files in organization.items():
        for filename in files:
            src = base / filename
            dest = base / dest_dir / filename
            
            if src.exists():
                try:
                    shutil.move(str(src), str(dest))
                    moved_count += 1
                    print(f"   ✓ {filename} → {dest_dir}")
                except Exception as e:
                    print(f"   ✗ Failed to move {filename}: {e}")
    
    print(f"\n   Total files moved: {moved_count}")
    
    # Keep these in root (important working files)
    keep_in_root = [
        'order6_link_compressor.py',  # Latest breakthrough
        'test_order6_links.py',  # Latest test
        'wiki_parser.py',  # Core utility
        'arithmetic_coder.py',  # Core utility
        'context_model.py',  # Core utility
        'download_enwik.py',  # Utility
        'download_enwik_auto.py',  # Utility
        'show_results.py',  # Utility
        'organize_repo.py',  # This script
    ]
    
    print("\n3️⃣ Files kept in root:")
    for f in keep_in_root:
        if (base / f).exists():
            print(f"   ✓ {f}")
    
    print("\n" + "=" * 70)
    print("✅ ORGANIZATION COMPLETE!")
    print("=" * 70)
    
    # Print new structure
    print("\n📁 NEW STRUCTURE:")
    print("""
    HutterLab/
    ├── README.md                    ← Main entry point
    ├── papers/                      ← Research papers
    │   ├── bigram_links_draft.md
    │   ├── zkp_properties_lessons_learned.md
    │   └── ...
    ├── docs/                        ← Important documentation
    │   ├── TODAY_COMPLETE_SUMMARY.md
    │   └── WORLD_RECORD_ROADMAP.md
    ├── experiments/                 ← All experimental code
    │   ├── analysis/               ← Analysis scripts
    │   ├── tests/                  ← Test scripts
    │   ├── exploratory/            ← Compressor experiments
    │   └── zkp_research/           ← ZKP research files
    ├── archive/                     ← Historical files
    │   ├── sessions/               ← Session summaries
    │   ├── old_docs/               ← Old documentation
    │   └── results/                ← Result files
    ├── data/                        ← Data files
    │   └── enwik_10mb
    └── [Core files]                 ← Latest working code
        ├── order6_link_compressor.py
        ├── test_order6_links.py
        └── ...
    """)
    
    print("\n💡 For random visitor:")
    print("   1. Start with README.md")
    print("   2. Check papers/ for research")
    print("   3. See docs/ for documentation")
    print("   4. Explore experiments/ if interested")
    print("   5. Archive/ has history (optional)")
    
    print("\n✨ Much cleaner now! 🎯")

if __name__ == "__main__":
    organize_repository()
