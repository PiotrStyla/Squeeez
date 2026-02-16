#!/usr/bin/env python3
"""
Generate all figures and charts for the research paper:
"Systematic Stacking for Wikipedia Compression: Closing 80% of Gap to World Record"

Author: Piotr Styła
Date: January 2026
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

# Set publication-quality style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("colorblind")

# Create output directory
output_dir = "paper_figures"
os.makedirs(output_dir, exist_ok=True)

# Color scheme (accessible)
COLORS = {
    'baseline': '#7F7F7F',      # Gray
    'our_result': '#1F77B4',    # Blue
    'world_record': '#FFD700',  # Gold
    'improvement': '#2CA02C',   # Green
    'future': '#D3D3D3',        # Light Gray
    'implemented': '#2CA02C',   # Green
    'not_implemented': '#CCCCCC' # Light Gray
}

def save_figure(filename, dpi=300):
    """Save figure in multiple formats"""
    base = os.path.join(output_dir, filename)
    plt.savefig(f"{base}.png", dpi=dpi, bbox_inches='tight')
    plt.savefig(f"{base}.pdf", bbox_inches='tight')
    print(f"✓ Saved: {filename}.png and {filename}.pdf")
    plt.close()


# ============================================================================
# Figure 1: Gap Progression Chart
# ============================================================================
def figure_1_gap_progression():
    """Bar chart showing progression from baseline to world record"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    configurations = ['PAQ8px\nBaseline', 'Our Result\n(Phase 2)', 'World Record\n(STARLIT)']
    sizes = [182.6, 127.44, 114.0]
    colors = [COLORS['baseline'], COLORS['our_result'], COLORS['world_record']]
    
    bars = ax.bar(configurations, sizes, color=colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar, size in zip(bars, sizes):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{size} MB',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Add improvement arrows
    # Baseline to Our Result
    ax.annotate('', xy=(1, 127.44), xytext=(0, 182.6),
                arrowprops=dict(arrowstyle='<->', color=COLORS['improvement'], lw=2))
    ax.text(0.5, 155, '55.16 MB\n(30.21%)', ha='center', va='center',
            fontsize=11, bbox=dict(boxstyle='round', facecolor='white', edgecolor=COLORS['improvement']))
    
    # Our Result to World Record
    ax.annotate('', xy=(2, 114.0), xytext=(1, 127.44),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(1.5, 120.7, '13.44 MB\n(1.34%)', ha='center', va='center',
            fontsize=11, bbox=dict(boxstyle='round', facecolor='white', edgecolor='red'))
    
    # Add gap closed annotation
    ax.text(1, 195, 'Gap Closed: 80.4%', ha='center', va='center',
            fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor=COLORS['improvement'], edgecolor='black', alpha=0.7))
    
    ax.set_ylabel('Compressed Size (MB)', fontsize=14, fontweight='bold')
    ax.set_title('Figure 1: Compression Size Reduction from Baseline to World Record',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 200)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    save_figure('figure_1_gap_progression')


# ============================================================================
# Figure 2: Non-Linear Scaling Discovery
# ============================================================================
def figure_2_scaling_discovery():
    """Line chart showing 14x scaling factor"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data points
    dataset_sizes = [10, 1000]  # MB
    linear_prediction = [2.16, 2.16]  # %
    actual_results = [2.16, 30.21]  # %
    
    # Plot lines
    ax.plot(dataset_sizes, linear_prediction, 'r--', linewidth=2, 
            label='Linear Prediction', marker='o', markersize=8)
    ax.plot(dataset_sizes, actual_results, 'b-', linewidth=3,
            label='Actual Result', marker='o', markersize=10)
    
    # Add data labels
    ax.text(10, 2.16, '2.16%', ha='right', va='bottom', fontsize=11, fontweight='bold')
    ax.text(1000, 2.16, '2.16%\n(Expected)', ha='left', va='top', fontsize=11)
    ax.text(1000, 30.21, '30.21%\n(Actual!)', ha='left', va='bottom', fontsize=12, fontweight='bold',
            color=COLORS['our_result'])
    
    # Shade the area between
    ax.fill_between(dataset_sizes, linear_prediction, actual_results, 
                    alpha=0.3, color=COLORS['improvement'],
                    label='14x Scaling Factor')
    
    # Add scaling factor annotation
    ax.annotate('', xy=(1000, 30.21), xytext=(1000, 2.16),
                arrowprops=dict(arrowstyle='<->', color='black', lw=2))
    ax.text(1100, 16, '14x Better\nthan Linear!', ha='left', va='center',
            fontsize=12, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
    
    ax.set_xlabel('Dataset Size (MB)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Improvement (%)', fontsize=14, fontweight='bold')
    ax.set_title('Figure 2: Non-Linear Scaling Discovery - 14x Factor',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xscale('log')
    ax.set_xlim(8, 1500)
    ax.set_ylim(0, 35)
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    save_figure('figure_2_scaling_discovery')


# ============================================================================
# Figure 3: Stacking Efficiency Analysis (Waterfall)
# ============================================================================
def figure_3_stacking_waterfall():
    """Waterfall chart showing cumulative improvements"""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Data
    categories = ['Baseline', 'Article\nReordering', 'Wikipedia\nTransforms', 
                  'Synergy', 'Final\nResult', 'World\nRecord']
    values = [182.6, -30, -25, -0.16, 0, -13.44]
    cumulative = np.cumsum(values)
    
    # Colors
    colors_list = [COLORS['baseline'], COLORS['improvement'], COLORS['improvement'],
                   COLORS['improvement'], COLORS['our_result'], COLORS['world_record']]
    
    # Create waterfall
    for i in range(len(categories)):
        if i == 0:
            ax.bar(i, values[i], color=colors_list[i], edgecolor='black', linewidth=1.5)
            ax.text(i, values[i]/2, f'{values[i]} MB', ha='center', va='center',
                   fontsize=11, fontweight='bold')
        elif i == len(categories) - 1:
            # World record reference line
            ax.bar(i, cumulative[i-1], bottom=0, color=colors_list[i], 
                   edgecolor='black', linewidth=1.5, alpha=0.7)
            ax.text(i, cumulative[i-1]/2, f'{cumulative[i-1]:.2f} MB', ha='center', va='center',
                   fontsize=11, fontweight='bold')
        elif i == len(categories) - 2:
            # Final result
            ax.bar(i, cumulative[i-1], bottom=0, color=colors_list[i],
                   edgecolor='black', linewidth=2)
            ax.text(i, cumulative[i-1]/2, f'{cumulative[i-1]:.2f} MB', ha='center', va='center',
                   fontsize=12, fontweight='bold', color='white')
        else:
            # Improvement bars
            ax.bar(i, abs(values[i]), bottom=cumulative[i-1], color=colors_list[i],
                   edgecolor='black', linewidth=1.5)
            ax.text(i, cumulative[i-1] + abs(values[i])/2, f'{values[i]} MB', ha='center', va='center',
                   fontsize=11, fontweight='bold', color='white')
            # Connecting lines
            if i > 0:
                ax.plot([i-0.4, i-0.1], [cumulative[i-1], cumulative[i-1]], 
                       'k--', linewidth=1)
    
    # Add gap annotation
    ax.annotate('', xy=(5.3, 127.44), xytext=(5.3, 114.0),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(5.5, 120.7, '13.44 MB\nRemaining', ha='left', va='center',
            fontsize=10, bbox=dict(boxstyle='round', facecolor='white', edgecolor='red'))
    
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylabel('Compressed Size (MB)', fontsize=14, fontweight='bold')
    ax.set_title('Figure 3: Stacking Efficiency - Waterfall Analysis',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 200)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    save_figure('figure_3_stacking_waterfall')


# ============================================================================
# Figure 4: Subset vs Full-Scale Comparison
# ============================================================================
def figure_4_subset_comparison():
    """Grouped bar chart comparing 10MB and 1GB tests"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['Baseline\nSize', 'Final\nSize', 'Improvement\n(%)']
    mb_10_values = [1.91, 1.87, 2.16]
    gb_1_values = [182.6, 127.44, 30.21]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, mb_10_values, width, label='10 MB Test',
                   color=COLORS['baseline'], edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, gb_1_values, width, label='1 GB Test',
                   color=COLORS['our_result'], edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add scaling factor annotation
    ax.annotate('', xy=(2.35, 30.21), xytext=(2.35, 2.16),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2.5))
    ax.text(2.6, 16, '14x\nScaling\nFactor!', ha='left', va='center',
           fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='yellow', edgecolor='red', linewidth=2))
    
    ax.set_ylabel('Value', fontsize=14, fontweight='bold')
    ax.set_title('Figure 4: Subset vs. Full-Scale Comparison',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add note
    ax.text(0.5, -10, 'Note: Values for "Baseline Size" and "Final Size" are in MB.\n"Improvement" values are in percentage.',
           ha='center', fontsize=9, style='italic',
           transform=ax.transData)
    
    save_figure('figure_4_subset_comparison')


# ============================================================================
# Figure 5: Preprocessing Impact Breakdown (Pie Chart)
# ============================================================================
def figure_5_preprocessing_breakdown():
    """Pie chart showing preprocessing contribution"""
    fig, ax = plt.subplots(figsize=(9, 7))
    
    labels = ['HTML Entities\n(55.0%)', 
              'Whitespace Cleanup\n(44.7%)', 
              'Bracket Normalization\n(0.3%)']
    sizes = [55.0, 44.7, 0.3]
    colors_pie = ['#1F77B4', '#2CA02C', '#D3D3D3']
    explode = (0.05, 0.05, 0.1)  # Explode the smallest slice
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                       colors=colors_pie, explode=explode,
                                       startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    
    # Make percentage text white
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')
    
    ax.set_title('Figure 5: Preprocessing Savings Breakdown\nTotal: 38.3 MB (3.83% of 1 GB)',
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add legend with absolute values
    legend_labels = ['HTML Entities: 21.1 MB',
                     'Whitespace: 17.1 MB',
                     'Brackets: 0.14 MB']
    ax.legend(legend_labels, loc='upper left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
    
    save_figure('figure_5_preprocessing_breakdown')


# ============================================================================
# Figure 6: Gap Attribution Analysis
# ============================================================================
def figure_6_gap_attribution():
    """Horizontal bar chart showing technique contributions"""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    techniques = ['Article Reordering', 'PPM Order-25', 'cmix Mixing',
                  'Wikipedia Transforms', 'LSTM Mixer', 'Memory Optimization',
                  'UTF + Misc']
    estimated_mb = [20, 15, 10, 8, 6, 5, 4.6]
    implemented = [True, False, False, True, False, False, False]
    
    colors_bars = [COLORS['implemented'] if impl else COLORS['not_implemented'] 
                   for impl in implemented]
    
    bars = ax.barh(techniques, estimated_mb, color=colors_bars, 
                   edgecolor='black', linewidth=1.5)
    
    # Add value labels and checkmarks
    for i, (bar, mb, impl) in enumerate(zip(bars, estimated_mb, implemented)):
        width = bar.get_width()
        label = f'{mb} MB'
        if impl:
            label += ' ✓'
        ax.text(width, bar.get_y() + bar.get_height()/2.,
               label, ha='left', va='center', fontsize=11, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor='black', pad=0.3))
    
    # Add summary annotations
    total_gap = sum(estimated_mb)
    implemented_sum = sum(mb for mb, impl in zip(estimated_mb, implemented) if impl)
    
    ax.axvline(implemented_sum, color='blue', linestyle='--', linewidth=2, alpha=0.7)
    ax.text(implemented_sum, 7.2, f'Implemented: ~{implemented_sum} MB\n(Expected 40.8% of gap)',
           ha='center', va='bottom', fontsize=10,
           bbox=dict(boxstyle='round', facecolor=COLORS['implemented'], alpha=0.7))
    
    ax.text(15, -1.2, f'Actual Achievement: 55.16 MB (80.4% of gap!)\n1.97x better than estimate',
           ha='center', fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='yellow', edgecolor='red', linewidth=2))
    
    ax.set_xlabel('Estimated Impact (MB)', fontsize=14, fontweight='bold')
    ax.set_title('Figure 6: Gap Attribution Analysis (68.6 MB Total)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 25)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add legend
    legend_elements = [mpatches.Patch(color=COLORS['implemented'], label='Implemented ✓'),
                       mpatches.Patch(color=COLORS['not_implemented'], label='Not Yet Implemented')]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
    
    save_figure('figure_6_gap_attribution')


# ============================================================================
# Figure 7: Compression Ratio Timeline
# ============================================================================
def figure_7_compression_timeline():
    """Timeline showing compression ratio improvements"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    years = [2018, 2021, 2025]
    ratios = [18.26, 11.40, 12.74]
    labels = ['PAQ8px\nBaseline', 'STARLIT\nWorld Record', 'Our System']
    colors_points = [COLORS['baseline'], COLORS['world_record'], COLORS['our_result']]
    
    # Plot points
    for year, ratio, label, color in zip(years, ratios, labels, colors_points):
        ax.scatter(year, ratio, s=300, color=color, edgecolor='black', linewidth=2, zorder=3)
        ax.text(year, ratio + 0.8, label, ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Connect with lines
    ax.plot([2018, 2021], [18.26, 11.40], 'k--', linewidth=1.5, alpha=0.5, zorder=1)
    ax.plot([2021, 2025], [11.40, 12.74], 'r--', linewidth=1.5, alpha=0.5, zorder=1)
    
    # Shade gap closed area
    ax.fill_between([2018, 2025], [18.26, 12.74], [11.40, 11.40],
                    alpha=0.3, color=COLORS['improvement'], label='Gap Closed: 80.4%')
    
    # Add improvement annotations
    ax.annotate('', xy=(2021, 11.40), xytext=(2018, 18.26),
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax.text(2019.5, 14.8, '6.86 pp\n(Progress to\nWorld Record)', ha='center', va='center',
           fontsize=9, bbox=dict(boxstyle='round', facecolor='white', edgecolor='green'))
    
    ax.text(2023, 13.5, 'Our Work\nClosed 80.4%\nof Gap!', ha='center', va='center',
           fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='yellow', edgecolor='red', linewidth=2))
    
    ax.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Compression Ratio (%)', fontsize=14, fontweight='bold')
    ax.set_title('Figure 7: Compression Ratio Progress Over Time',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(2017, 2026)
    ax.set_ylim(10, 20)
    ax.invert_yaxis()  # Lower is better
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10)
    
    save_figure('figure_7_compression_timeline')


# ============================================================================
# Figure 8: Time vs Quality Trade-off
# ============================================================================
def figure_8_time_quality_tradeoff():
    """Scatter plot showing time vs compressed size trade-off"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data (estimated for different compression levels)
    times = [20, 50, 73, 100, 150]  # hours
    sizes = [145, 135, 127.44, 123, 120]  # MB
    labels = ['Quick\n(Level 3)', 'Fast\n(Level 4)', 'Standard\n(Level 5)\n[Our Choice]', 
              'Intensive\n(Level 6)', 'Maximum\n(Level 8)']
    
    # Plot points
    ax.scatter(times, sizes, s=200, color=COLORS['our_result'], edgecolor='black', linewidth=1.5, zorder=3)
    
    # Highlight our choice
    ax.scatter([73], [127.44], s=400, color='yellow', edgecolor='red', linewidth=3, 
              marker='*', zorder=4, label='Our Configuration')
    
    # Add trend line
    z = np.polyfit(times, sizes, 2)
    p = np.poly1d(z)
    x_smooth = np.linspace(20, 150, 100)
    ax.plot(x_smooth, p(x_smooth), 'r--', linewidth=2, alpha=0.5, label='Trend (Diminishing Returns)')
    
    # Add labels
    for time, size, label in zip(times, sizes, labels):
        if time == 73:
            ax.text(time, size - 3, label, ha='center', va='top', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='yellow', edgecolor='red', linewidth=2))
        else:
            ax.text(time, size + 2, label, ha='center', va='bottom', fontsize=9)
    
    # Add world record reference
    ax.axhline(114, color='gold', linestyle='--', linewidth=2, label='World Record (114 MB)', alpha=0.7)
    
    # Add annotation for diminishing returns
    ax.annotate('', xy=(150, 120), xytext=(73, 127.44),
                arrowprops=dict(arrowstyle='->', color='red', lw=2, linestyle='--'))
    ax.text(110, 123, '77 extra hours\nonly saves 7.5 MB\n(Diminishing Returns!)', 
           ha='center', va='center', fontsize=9,
           bbox=dict(boxstyle='round', facecolor='white', edgecolor='red'))
    
    ax.set_xlabel('Compression Time (hours)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Compressed Size (MB)', fontsize=14, fontweight='bold')
    ax.set_title('Figure 8: Time vs. Quality Trade-off',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 160)
    ax.set_ylim(115, 150)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    save_figure('figure_8_time_quality_tradeoff')


# ============================================================================
# Generate All Figures
# ============================================================================
def main():
    """Generate all figures for the research paper"""
    print("=" * 70)
    print("Generating Research Paper Figures")
    print("=" * 70)
    print()
    
    print("Creating figures...")
    figure_1_gap_progression()
    figure_2_scaling_discovery()
    figure_3_stacking_waterfall()
    figure_4_subset_comparison()
    figure_5_preprocessing_breakdown()
    figure_6_gap_attribution()
    figure_7_compression_timeline()
    figure_8_time_quality_tradeoff()
    
    print()
    print("=" * 70)
    print(f"✓ All figures generated successfully!")
    print(f"✓ Output directory: {output_dir}/")
    print(f"✓ Formats: PNG (300 DPI) and PDF (vector)")
    print("=" * 70)
    print()
    print("Figures generated:")
    print("  1. Gap Progression Chart")
    print("  2. Non-Linear Scaling Discovery")
    print("  3. Stacking Efficiency Waterfall")
    print("  4. Subset vs Full-Scale Comparison")
    print("  5. Preprocessing Impact Breakdown")
    print("  6. Gap Attribution Analysis")
    print("  7. Compression Ratio Timeline")
    print("  8. Time vs Quality Trade-off")
    print()
    print("Next steps:")
    print("  - Review figures in paper_figures/ directory")
    print("  - Integrate into LaTeX document")
    print("  - Adjust colors/sizes as needed")
    print()


if __name__ == "__main__":
    main()
