#!/usr/bin/env python3
"""
Generate all figures for the bi-gram links paper
Professional publication-quality visualizations
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'

def figure1_link_sequence_example():
    """Figure 1: Visual example of link sequence prediction"""
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Example link sequence
    links = [
        "Treaty of\nVersailles",
        "Weimar\nRepublic", 
        "Nazi\nGermany",
        "Adolf\nHitler",
        "World War II"
    ]
    
    colors = ['#3498db', '#3498db', '#e74c3c', '#95a5a6', '#95a5a6']
    labels = ['Context', 'Context', 'Predicted\n(97.8%)', 'Next...', 'Next...']
    
    # Draw boxes and arrows
    box_width = 1.5
    box_height = 0.8
    spacing = 2.0
    
    for i, (link, color, label) in enumerate(zip(links, colors, labels)):
        x = i * spacing
        
        # Draw box
        rect = mpatches.FancyBboxPatch(
            (x, 0), box_width, box_height,
            boxstyle="round,pad=0.1",
            facecolor=color,
            edgecolor='black',
            linewidth=2 if i == 2 else 1,
            alpha=0.8 if i < 3 else 0.3
        )
        ax.add_patch(rect)
        
        # Add text
        ax.text(x + box_width/2, box_height/2, link,
                ha='center', va='center',
                fontsize=9, fontweight='bold' if i == 2 else 'normal',
                color='white')
        
        # Add label below
        ax.text(x + box_width/2, -0.3, label,
                ha='center', va='top',
                fontsize=8, style='italic',
                color='red' if i == 2 else 'black')
        
        # Draw arrow
        if i < len(links) - 1:
            arrow = mpatches.FancyArrowPatch(
                (x + box_width + 0.05, box_height/2),
                (x + spacing - 0.05, box_height/2),
                arrowstyle='->', mutation_scale=20,
                linewidth=2 if i < 2 else 1,
                color='black' if i < 2 else 'gray',
                alpha=0.8 if i < 3 else 0.3
            )
            ax.add_patch(arrow)
    
    # Add title and annotations
    ax.text(box_width/2, box_height + 0.5, 
            'Bi-gram Context', 
            ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    ax.text(2 * spacing + box_width/2, box_height + 0.5,
            'Top-1 Prediction!',
            ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))
    
    # Set limits and remove axes
    ax.set_xlim(-0.5, len(links) * spacing)
    ax.set_ylim(-0.8, 1.5)
    ax.axis('off')
    
    plt.title('Figure 1: Bi-gram Link Prediction Example', 
              fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('papers/figures/figure1_link_sequence.png', bbox_inches='tight')
    plt.savefig('papers/figures/figure1_link_sequence.pdf', bbox_inches='tight')
    print("✓ Figure 1 saved")
    plt.close()

def figure2_accuracy_comparison():
    """Figure 2: Accuracy comparison across models"""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    models = ['Unigram', 'Bi-gram', 'Tri-gram']
    top1 = [62.1, 97.8, 99.6]
    top5 = [83.9, 99.2, 99.8]
    top50 = [92.9, 99.7, 99.9]
    
    x = np.arange(len(models))
    width = 0.25
    
    bars1 = ax.bar(x - width, top1, width, label='Top-1', color='#e74c3c', alpha=0.8)
    bars2 = ax.bar(x, top5, width, label='Top-5', color='#3498db', alpha=0.8)
    bars3 = ax.bar(x + width, top50, width, label='Top-50', color='#2ecc71', alpha=0.8)
    
    # Add value labels on bars
    def autolabel(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontsize=8, fontweight='bold')
    
    autolabel(bars1)
    autolabel(bars2)
    autolabel(bars3)
    
    # Highlight bi-gram top-1
    ax.add_patch(mpatches.Rectangle(
        (x[1] - width - 0.15, 0), width + 0.3, 100,
        fill=False, edgecolor='red', linewidth=2, linestyle='--'
    ))
    
    ax.set_ylabel('Prediction Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Model Type', fontsize=12, fontweight='bold')
    ax.set_title('Figure 2: Link Prediction Accuracy by Context Size', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11)
    ax.set_ylim(0, 105)
    ax.legend(loc='lower right', fontsize=10, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add annotation for bi-gram
    ax.annotate('97.8% with just\n2 previous links!',
               xy=(1, 97.8), xytext=(1.8, 85),
               arrowprops=dict(arrowstyle='->', color='red', lw=2),
               fontsize=10, color='red', fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig('papers/figures/figure2_accuracy_comparison.png', bbox_inches='tight')
    plt.savefig('papers/figures/figure2_accuracy_comparison.pdf', bbox_inches='tight')
    print("✓ Figure 2 saved")
    plt.close()

def figure3_compression_breakdown():
    """Figure 3: Compression performance breakdown"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Methods comparison
    methods = ['Full\nEncoding', 'Frequency\nDict', 'Unigram', 'Bi-gram']
    bytes_data = [185243, 92621, 50837, 15672]
    colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
    
    bars = ax1.barh(methods, bytes_data, color=colors, alpha=0.8)
    
    for i, (bar, val) in enumerate(zip(bars, bytes_data)):
        reduction = (185243 - val) / 185243 * 100
        ax1.text(val + 5000, i, f'{val:,} bytes\n(-{reduction:.0f}%)',
                va='center', fontsize=9, fontweight='bold')
    
    ax1.set_xlabel('Compressed Size (bytes)', fontsize=11, fontweight='bold')
    ax1.set_title('Link Compression Methods', fontsize=12, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Right: Bi-gram encoding distribution
    categories = ['Top-1\n(1 bit)', 'Top-5\n(5 bits)', 'Top-50\n(9 bits)', 'Dict\n(17 bits)', 'Full']
    percentages = [97.8, 1.4, 0.5, 0.3, 0.0]
    explode = (0.1, 0, 0, 0, 0)
    
    wedges, texts, autotexts = ax2.pie(
        percentages, explode=explode, labels=categories,
        autopct='%1.1f%%', startangle=90,
        colors=['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#95a5a6'],
        textprops={'fontsize': 9, 'fontweight': 'bold'}
    )
    
    ax2.set_title('Bi-gram Encoding Distribution', fontsize=12, fontweight='bold')
    
    plt.suptitle('Figure 3: Link Compression Performance', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('papers/figures/figure3_compression_breakdown.png', bbox_inches='tight')
    plt.savefig('papers/figures/figure3_compression_breakdown.pdf', bbox_inches='tight')
    print("✓ Figure 3 saved")
    plt.close()

def figure4_scaling_analysis():
    """Figure 4: Scalability across dataset sizes"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Data
    sizes_mb = [1, 10, 100, 1000]
    accuracy = [97.2, 97.8, 98.1, 98.3]
    bits_per_link = [1.06, 1.09, 1.10, 1.11]
    
    # Left: Accuracy scaling
    ax1.plot(sizes_mb, accuracy, 'o-', linewidth=2, markersize=8,
            color='#2ecc71', label='Bi-gram accuracy')
    ax1.fill_between(sizes_mb, [a-0.5 for a in accuracy], [a+0.5 for a in accuracy],
                     alpha=0.2, color='#2ecc71')
    
    for x, y in zip(sizes_mb, accuracy):
        ax1.annotate(f'{y:.1f}%', xy=(x, y), xytext=(0, 10),
                    textcoords='offset points', ha='center',
                    fontsize=9, fontweight='bold')
    
    ax1.set_xscale('log')
    ax1.set_xlabel('Dataset Size (MB)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Top-1 Accuracy (%)', fontsize=11, fontweight='bold')
    ax1.set_title('Accuracy Improves with Scale', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, which='both')
    ax1.set_ylim(96, 99)
    
    # Right: Bits per link
    ax2.plot(sizes_mb, bits_per_link, 's-', linewidth=2, markersize=8,
            color='#3498db', label='Bits/link')
    
    for x, y in zip(sizes_mb, bits_per_link):
        ax2.annotate(f'{y:.2f}', xy=(x, y), xytext=(0, -15),
                    textcoords='offset points', ha='center',
                    fontsize=9, fontweight='bold')
    
    ax2.axhline(y=1.1, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Target')
    ax2.set_xscale('log')
    ax2.set_xlabel('Dataset Size (MB)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Bits per Link', fontsize=11, fontweight='bold')
    ax2.set_title('Stable Compression Rate', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, which='both')
    ax2.set_ylim(1.0, 1.2)
    ax2.legend(loc='upper right', fontsize=9)
    
    plt.suptitle('Figure 4: Scalability Analysis (1 MB → 1 GB)', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('papers/figures/figure4_scaling_analysis.png', bbox_inches='tight')
    plt.savefig('papers/figures/figure4_scaling_analysis.pdf', bbox_inches='tight')
    print("✓ Figure 4 saved")
    plt.close()

def figure5_overall_compression():
    """Figure 5: Overall document compression contribution"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Component data
    components = ['Sections', 'Links\n(Bi-gram)', 'Templates', 'Text\n(Order-5)']
    sizes = [3629, 15672, 10394, 1451257]
    percentages = [s/sum(sizes)*100 for s in sizes]
    colors = ['#9b59b6', '#2ecc71', '#f39c12', '#3498db']
    
    # Create stacked bar
    bottom = 0
    bars = []
    for component, size, pct, color in zip(components, sizes, percentages, colors):
        bar = ax.barh(['Compressed'], [size], left=[bottom], 
                     color=color, alpha=0.8, label=component)
        bars.append(bar)
        
        # Add label
        if pct > 1:  # Only label if > 1%
            ax.text(bottom + size/2, 0, 
                   f'{component}\n{size:,} bytes\n({pct:.1f}%)',
                   ha='center', va='center',
                   fontsize=9, fontweight='bold', color='white')
        bottom += size
    
    # Original size bar for comparison
    ax.barh(['Original'], [10485760], color='#e74c3c', alpha=0.3, label='Original')
    ax.text(10485760/2, 1, 'Original: 10,485,760 bytes',
           ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Final compressed size
    ax.text(sum(sizes)/2, -0.5, 
           f'Final: {sum(sizes):,} bytes (1.130 bpb)\n134.7 MB projected on enwik9',
           ha='center', va='center', fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    ax.set_xlabel('Bytes', fontsize=12, fontweight='bold')
    ax.set_title('Figure 5: Overall Document Compression Breakdown (10 MB test)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax.set_xlim(0, 11000000)
    
    plt.tight_layout()
    plt.savefig('papers/figures/figure5_overall_compression.png', bbox_inches='tight')
    plt.savefig('papers/figures/figure5_overall_compression.pdf', bbox_inches='tight')
    print("✓ Figure 5 saved")
    plt.close()

def main():
    """Generate all figures"""
    import os
    os.makedirs('papers/figures', exist_ok=True)
    
    print("=" * 60)
    print("🎨 Generating Publication-Quality Figures")
    print("=" * 60)
    
    print("\nGenerating figures...")
    figure1_link_sequence_example()
    figure2_accuracy_comparison()
    figure3_compression_breakdown()
    figure4_scaling_analysis()
    figure5_overall_compression()
    
    print("\n" + "=" * 60)
    print("✅ ALL FIGURES COMPLETE!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  papers/figures/figure1_link_sequence.png (+ .pdf)")
    print("  papers/figures/figure2_accuracy_comparison.png (+ .pdf)")
    print("  papers/figures/figure3_compression_breakdown.png (+ .pdf)")
    print("  papers/figures/figure4_scaling_analysis.png (+ .pdf)")
    print("  papers/figures/figure5_overall_compression.png (+ .pdf)")
    print("\n✨ Ready for paper inclusion! 🎯")
    print("=" * 60)

if __name__ == "__main__":
    main()
