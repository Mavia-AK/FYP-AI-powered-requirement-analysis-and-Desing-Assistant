"""
Generate visualization charts for model results poster
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
colors = ['#2E86AB', '#A23B72', '#F18F01']  # Professional color palette

# Load results
with open('evaluation/ambiguity_classification_report.json', 'r') as f:
    class_report = json.load(f)

with open('evaluation/ambiguity_test_results.json', 'r') as f:
    test_results = json.load(f)

# Create output directory
Path('visualizations').mkdir(exist_ok=True)

# ============== Chart 1: Per-Class Metrics Comparison ==============
fig, ax = plt.subplots(figsize=(14, 8))

classes = ['Clear Requirements', 'Ambiguous Requirements']
metrics = ['Precision', 'Recall', 'F1-Score']
x = np.arange(len(classes))
width = 0.25

precision_scores = [class_report['Clear']['precision'] * 100, 
                    class_report['Ambiguous']['precision'] * 100]
recall_scores = [class_report['Clear']['recall'] * 100, 
                 class_report['Ambiguous']['recall'] * 100]
f1_scores = [class_report['Clear']['f1-score'] * 100, 
             class_report['Ambiguous']['f1-score'] * 100]

bars1 = ax.bar(x - width, precision_scores, width, label='Precision', color='#2E86AB', alpha=0.85, edgecolor='black', linewidth=1.2)
bars2 = ax.bar(x, recall_scores, width, label='Recall', color='#A23B72', alpha=0.85, edgecolor='black', linewidth=1.2)
bars3 = ax.bar(x + width, f1_scores, width, label='F1-Score', color='#F18F01', alpha=0.85, edgecolor='black', linewidth=1.2)

ax.set_xlabel('Classification Type', fontsize=14, fontweight='bold')
ax.set_ylabel('Performance Score (%)', fontsize=14, fontweight='bold')
ax.set_title('Per-Class Performance Metrics Comparison\nAmbiguity Classification Model', fontsize=16, fontweight='bold', pad=25)
ax.set_xticks(x)
ax.set_xticklabels(classes, fontsize=13, fontweight='bold')
ax.legend(fontsize=13, loc='lower right', framealpha=0.95)
ax.set_ylim([90, 100])
ax.grid(axis='y', alpha=0.4, linestyle='--')
ax.tick_params(axis='y', labelsize=12)

# Add value labels on bars
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{height:.2f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('visualizations/01_per_class_metrics.png', dpi=300, bbox_inches='tight')
print("✓ Created: 01_per_class_metrics.png")
plt.close()

# ============== Chart 2: Overall Metrics Dashboard ==============
fig, ax = plt.subplots(figsize=(12, 7))

overall_metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
overall_values = [
    test_results['eval_accuracy'] * 100,
    test_results['eval_precision'] * 100,
    test_results['eval_recall'] * 100,
    test_results['eval_f1'] * 100,
    test_results['eval_roc_auc'] * 100
]

bars = ax.barh(overall_metrics, overall_values, color=colors + ['#06A77D', '#D62828'], 
               edgecolor='black', linewidth=1.2, alpha=0.85)
ax.set_xlabel('Performance Score (%)', fontsize=14, fontweight='bold')
ax.set_title('Overall Model Performance Metrics - Test Results\nEvaluation on 1,682 Test Samples', 
             fontsize=16, fontweight='bold', pad=25)
ax.set_xlim([90, 100])
ax.grid(axis='x', alpha=0.4, linestyle='--')
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=12)

# Make metric names bold
for label in ax.get_yticklabels():
    label.set_fontweight('bold')

# Add value labels
for i, (bar, value) in enumerate(zip(bars, overall_values)):
    ax.text(value - 2, i, f'{value:.2f}%', 
            ha='right', va='center', fontsize=12, fontweight='bold', color='white')

plt.tight_layout()
plt.savefig('visualizations/02_overall_metrics.png', dpi=300, bbox_inches='tight')
print("✓ Created: 02_overall_metrics.png")
plt.close()

# ============== Chart 3: Class Distribution & Support ==============
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Support distribution
classes_list = ['Clear Requirements', 'Ambiguous Requirements']
support = [class_report['Clear']['support'], class_report['Ambiguous']['support']]
colors_pie = ['#2E86AB', '#A23B72']

wedges, texts, autotexts = ax1.pie(support, labels=classes_list, autopct='%1.1f%%',
                                     colors=colors_pie, startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'},
                                     wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})
ax1.set_title('Test Set Class Distribution\nTotal: 1,682 Samples', 
              fontsize=14, fontweight='bold', pad=20)

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(12)

# Support bars
bars = ax2.bar(classes_list, support, color=colors_pie, alpha=0.85, edgecolor='black', linewidth=1.5)
ax2.set_ylabel('Number of Test Samples', fontsize=13, fontweight='bold')
ax2.set_title('Test Set Sample Count by Class', fontsize=14, fontweight='bold', pad=20)
ax2.grid(axis='y', alpha=0.4, linestyle='--')
ax2.tick_params(axis='x', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)

for i, (bar, v) in enumerate(zip(bars, support)):
    ax2.text(i, v + 30, f'{int(v)} samples\n({v/sum(support)*100:.1f}%)', 
             ha='center', fontweight='bold', fontsize=12)

plt.tight_layout()
plt.savefig('visualizations/03_class_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Created: 03_class_distribution.png")
plt.close()

# ============== Chart 4: Weighted Averages Comparison ==============
fig, ax = plt.subplots(figsize=(12, 7))

weighted_metrics = ['Precision', 'Recall', 'F1-Score']
weighted_values = [
    class_report['weighted avg']['precision'] * 100,
    class_report['weighted avg']['recall'] * 100,
    class_report['weighted avg']['f1-score'] * 100
]
macro_values = [
    class_report['macro avg']['precision'] * 100,
    class_report['macro avg']['recall'] * 100,
    class_report['macro avg']['f1-score'] * 100
]

x = np.arange(len(weighted_metrics))
width = 0.38

bars1 = ax.bar(x - width/2, weighted_values, width, label='Weighted Average (Class-Balanced)', 
               color='#2E86AB', alpha=0.85, edgecolor='black', linewidth=1.2)
bars2 = ax.bar(x + width/2, macro_values, width, label='Macro Average (Unweighted)', 
               color='#F18F01', alpha=0.85, edgecolor='black', linewidth=1.2)

ax.set_ylabel('Performance Score (%)', fontsize=14, fontweight='bold')
ax.set_title('Averaged Model Performance Metrics\nWeighted vs Macro Average Comparison', 
             fontsize=16, fontweight='bold', pad=25)
ax.set_xticks(x)
ax.set_xticklabels(weighted_metrics, fontsize=13, fontweight='bold')
ax.legend(fontsize=13, loc='lower right', framealpha=0.95)
ax.set_ylim([94, 97])
ax.grid(axis='y', alpha=0.4, linestyle='--')
ax.tick_params(axis='y', labelsize=12)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.2f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('visualizations/04_weighted_macro_avg.png', dpi=300, bbox_inches='tight')
print("✓ Created: 04_weighted_macro_avg.png")
plt.close()

# ============== Chart 5: Key Metrics Heatmap ==============
fig, ax = plt.subplots(figsize=(11, 7))

# Create data matrix
data = np.array([
    [class_report['Clear']['precision'], class_report['Clear']['recall'], class_report['Clear']['f1-score']],
    [class_report['Ambiguous']['precision'], class_report['Ambiguous']['recall'], class_report['Ambiguous']['f1-score']]
]) * 100

im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=90, vmax=100)

# Set ticks and labels
ax.set_xticks(np.arange(3))
ax.set_yticks(np.arange(2))
ax.set_xticklabels(['Precision', 'Recall', 'F1-Score'], fontsize=13, fontweight='bold')
ax.set_yticklabels(['Clear Requirements', 'Ambiguous Requirements'], fontsize=13, fontweight='bold')

# Improve tick label visibility
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)

# Add colorbar with label
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Performance Score (%)', rotation=270, labelpad=25, fontsize=12, fontweight='bold')
cbar.ax.tick_params(labelsize=11)

# Add text annotations with borders
for i in range(2):
    for j in range(3):
        text = ax.text(j, i, f'{data[i, j]:.2f}%',
                      ha="center", va="center", color="black", 
                      fontweight='bold', fontsize=14, 
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7, edgecolor='black', linewidth=1))

ax.set_title('Performance Metrics Heatmap - Per-Class Analysis\nAmbiguity Classification Model', 
             fontsize=16, fontweight='bold', pad=25)
plt.tight_layout()
plt.savefig('visualizations/05_metrics_heatmap.png', dpi=300, bbox_inches='tight')
print("✓ Created: 05_metrics_heatmap.png")
plt.close()

print("\n✅ All visualizations generated successfully!")
print("📁 Location: visualizations/")
print("\nGenerated files:")
print("  1. 01_per_class_metrics.png - Precision, Recall, F1-Score by class")
print("  2. 02_overall_metrics.png - Overall performance dashboard")
print("  3. 03_class_distribution.png - Test set distribution")
print("  4. 04_weighted_macro_avg.png - Averaged metrics comparison")
print("  5. 05_metrics_heatmap.png - Heatmap visualization")
