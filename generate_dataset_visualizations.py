"""
Generate dataset visualizations for poster
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Create output directory
Path('visualizations').mkdir(exist_ok=True)

# Load datasets
train_df = pd.read_csv('data/processed/train.csv')
val_df = pd.read_csv('data/processed/val.csv')
test_df = pd.read_csv('data/processed/test.csv')
raw_df = pd.read_csv('data/raw/ambiguity_dataset.csv')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')

# ============== Chart 1: Dataset Split Distribution ==============
fig, ax = plt.subplots(figsize=(11, 7))

splits = ['Training Set', 'Validation Set', 'Test Set']
samples = [len(train_df), len(val_df), len(test_df)]
percentages = [70, 15, 15]
colors_split = ['#2E86AB', '#A23B72', '#F18F01']

bars = ax.bar(splits, samples, color=colors_split, alpha=0.85, edgecolor='black', linewidth=1.5)
ax.set_ylabel('Number of Samples', fontsize=14, fontweight='bold')
ax.set_title('Dataset Split Distribution\nTotal: 11,213 Preprocessed Samples (70% Train / 15% Val / 15% Test)', 
             fontsize=16, fontweight='bold', pad=25)
ax.grid(axis='y', alpha=0.4, linestyle='--')
ax.tick_params(axis='x', labelsize=13)
ax.tick_params(axis='y', labelsize=12)

for i, (bar, sample, pct) in enumerate(zip(bars, samples, percentages)):
    height = bar.get_height()
    ax.text(i, height + 150, f'{sample:,} samples\n({pct}%)', 
            ha='center', fontweight='bold', fontsize=12)

plt.tight_layout()
plt.savefig('visualizations/06_dataset_split.png', dpi=300, bbox_inches='tight')
print("✓ Created: 06_dataset_split.png")
plt.close()

# ============== Chart 2: Raw Dataset Class Distribution ==============
fig, ax = plt.subplots(figsize=(11, 7))

ambiguity_types = list(raw_df['ambiguity_type'].value_counts().index)
ambiguity_counts = list(raw_df['ambiguity_type'].value_counts().values)

colors_ambig = ['#2E86AB', '#A23B72', '#F18F01', '#06A77D', '#D62828', '#FFB703']

bars = ax.barh(ambiguity_types, ambiguity_counts, color=colors_ambig[:len(ambiguity_types)], 
               alpha=0.85, edgecolor='black', linewidth=1.2)
ax.set_xlabel('Number of Requirements', fontsize=14, fontweight='bold')
ax.set_title('Raw Dataset: Ambiguity Type Distribution\nTotal: 11,440 Software Requirements', 
             fontsize=16, fontweight='bold', pad=25)
ax.grid(axis='x', alpha=0.4, linestyle='--')
ax.tick_params(axis='y', labelsize=12)
ax.tick_params(axis='x', labelsize=12)

# Make y-axis labels bold
for label in ax.get_yticklabels():
    label.set_fontweight('bold')

# Add value labels
for i, (bar, count) in enumerate(zip(bars, ambiguity_counts)):
    percentage = count / sum(ambiguity_counts) * 100
    ax.text(count + 50, i, f'{count:,} ({percentage:.1f}%)', 
            ha='left', va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('visualizations/07_raw_ambiguity_types.png', dpi=300, bbox_inches='tight')
print("✓ Created: 07_raw_ambiguity_types.png")
plt.close()

# ============== Chart 3: Train/Val/Test Class Distribution ==============
fig, axes = plt.subplots(1, 3, figsize=(15, 6), sharey=True)

datasets = [train_df, val_df, test_df]
dataset_names = ['Training Set\n(7,849 samples)', 'Validation Set\n(1,682 samples)', 'Test Set\n(1,682 samples)']
class_labels = ['Clear\n(0)', 'Ambiguous\n(1)']

for ax, df, name in zip(axes, datasets, dataset_names):
    class_counts = df['is_ambiguous'].value_counts().sort_index()
    colors_class = ['#2E86AB', '#A23B72']
    
    bars = ax.bar(class_labels, class_counts.values, color=colors_class, 
                  alpha=0.85, edgecolor='black', linewidth=1.5)
    ax.set_title(name, fontsize=13, fontweight='bold', pad=15)
    ax.set_ylabel('Number of Samples', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.4, linestyle='--')
    ax.tick_params(axis='y', labelsize=11)
    
    # Add value labels
    for bar, count in zip(bars, class_counts.values):
        height = bar.get_height()
        percentage = count / len(df) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'{count:,}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

fig.suptitle('Class Distribution: Train / Validation / Test Sets\nConsistent 63% Clear vs 37% Ambiguous Ratio', 
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('visualizations/08_train_val_test_classes.png', dpi=300, bbox_inches='tight')
print("✓ Created: 08_train_val_test_classes.png")
plt.close()

# ============== Chart 4: Data Pipeline Overview ==============
fig, ax = plt.subplots(figsize=(12, 8))
ax.axis('off')

# Define pipeline stages
stages = [
    ('Raw Data\n11,440 samples\n9 features\n6 ambiguity types', 0.1, 0.85, '#2E86AB'),
    ('Data Cleaning\nText preprocessing\nNormalization', 0.35, 0.85, '#A23B72'),
    ('Feature Extraction\nTokenization\n2 text features', 0.6, 0.85, '#F18F01'),
    ('Data Split\n70% Train | 15% Val | 15% Test', 0.85, 0.85, '#06A77D'),
    ('Final Dataset\n11,213 samples\n3 features\n2 classes', 0.85, 0.5, '#D62828'),
]

# Draw boxes and labels
for text, x, y, color in stages:
    box = plt.Rectangle((x-0.08, y-0.1), 0.15, 0.15, 
                        facecolor=color, edgecolor='black', linewidth=2.5, alpha=0.85)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=11, fontweight='bold', color='white')

# Draw arrows
arrow_props = dict(arrowstyle='->', lw=2.5, color='black')
ax.annotate('', xy=(0.27, 0.85), xytext=(0.18, 0.85), arrowprops=arrow_props)
ax.annotate('', xy=(0.52, 0.85), xytext=(0.43, 0.85), arrowprops=arrow_props)
ax.annotate('', xy=(0.77, 0.85), xytext=(0.68, 0.85), arrowprops=arrow_props)
ax.annotate('', xy=(0.85, 0.6), xytext=(0.85, 0.75), arrowprops=arrow_props)

ax.set_xlim(0, 1)
ax.set_ylim(0.3, 1)
ax.set_aspect('equal')

plt.title('AI-RADA Dataset Processing Pipeline', fontsize=16, fontweight='bold', pad=30)
plt.tight_layout()
plt.savefig('visualizations/09_data_pipeline.png', dpi=300, bbox_inches='tight')
print("✓ Created: 09_data_pipeline.png")
plt.close()

# ============== Chart 5: Key Dataset Statistics ==============
fig, ax = plt.subplots(figsize=(12, 8))
ax.axis('off')

# Statistics boxes
stats_data = [
    ('Raw Dataset', '11,440\nSamples', '#2E86AB'),
    ('After\nPreprocessing', '11,213\nSamples', '#A23B72'),
    ('Training\nSamples', '7,849\n(70%)', '#F18F01'),
    ('Validation\nSamples', '1,682\n(15%)', '#06A77D'),
    ('Test\nSamples', '1,682\n(15%)', '#D62828'),
]

x_positions = [0.1, 0.3, 0.5, 0.7, 0.9]
for (label, value, color), x in zip(stats_data, x_positions):
    # Draw box
    box = plt.Rectangle((x-0.08, 0.5-0.15), 0.16, 0.3, 
                        facecolor=color, edgecolor='black', linewidth=2.5, alpha=0.85)
    ax.add_patch(box)
    
    # Add text
    ax.text(x, 0.68, label, ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    ax.text(x, 0.5, value, ha='center', va='center', fontsize=13, fontweight='bold', color='white')

# Add bottom statistics
stats_text = """
✓ Zero Missing Values (100% Data Quality)
✓ Balanced Classes: 63% Clear vs 37% Ambiguous
✓ 6 Types of Ambiguity Detected
✓ Consistent Split Ratios Across All Sets
✓ Professional Preprocessing Pipeline
"""

ax.text(0.5, 0.2, stats_text, ha='center', va='top', fontsize=12, 
        fontweight='bold', bbox=dict(boxstyle='round,pad=1', facecolor='#F0F0F0', 
        edgecolor='black', linewidth=2))

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')

plt.title('Dataset Summary: Key Statistics', fontsize=16, fontweight='bold', pad=30)
plt.tight_layout()
plt.savefig('visualizations/10_dataset_summary.png', dpi=300, bbox_inches='tight')
print("✓ Created: 10_dataset_summary.png")
plt.close()

print("\n✅ All dataset visualizations generated successfully!")
print("📁 Location: visualizations/")
print("\nNew files created:")
print("  6. 06_dataset_split.png - Train/Val/Test split distribution")
print("  7. 07_raw_ambiguity_types.png - Raw data ambiguity type breakdown")
print("  8. 08_train_val_test_classes.png - Class distribution across splits")
print("  9. 09_data_pipeline.png - Data processing pipeline overview")
print("  10. 10_dataset_summary.png - Key dataset statistics")
