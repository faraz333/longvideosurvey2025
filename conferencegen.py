import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set style
try:
    plt.style.use('seaborn')
except:
    plt.style.use('seaborn-v0_8')

# ===== USER-CUSTOMIZABLE DATA =====
years = ['2021', '2022', '2023', '2024', '2025']
conferences = ['arXiv', 'CVPR', 'ICLR', 'NeurIPS', 'IEEE-ICF', 'IEEE-TVCG',
               'VISIGRAPP', 'IEEE-ICP', 'PAVOD', 'IEEE-Multimedia',
               'ICML', 'ACM Multimedia', 'IEEE-WACV']

# Paper counts by year (rows) x conference (columns)
paper_counts = {
    '2021': [2, 2, 0, 1, 0, 0, 0, 0, 2, 0, 0, 0, 3],
    '2022': [5, 5, 9, 8, 5, 4, 5, 3, 5, 5, 7, 0, 5],
    '2023': [20, 30, 10, 5, 5, 4, 4, 3, 3, 5, 8, 7, 4],
    '2024': [30, 30, 10, 10, 5, 5, 5, 4, 5, 6, 9, 8, 5],
    '2025': [10, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Only arXiv/CVPR
}

# Convert to DataFrame
df = pd.DataFrame.from_dict(paper_counts, orient='index', columns=conferences)

# ===== PLOT CONFIGURATION =====
plt.figure(figsize=(12, 6))
colors = plt.cm.tab20.colors
bar_width = 0.5  # Adjusted to make bars narrower

# Stacked bars
bottom = np.zeros(len(years))
for i, conf in enumerate(conferences):
    counts = df[conf]
    if counts.sum() > 0:
        plt.bar(years, counts, width=bar_width,
                label=conf, bottom=bottom, color=colors[i])
        bottom += counts

# Add totals
for i, year in enumerate(years):
    total = df.loc[year].sum()
    plt.text(i, total + 15, f'{total}',
             ha='center', va='bottom', fontsize=10)

# Formatting
plt.title('AI Conference Papers (2021-2025)', fontsize=14, pad=20)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Papers Published', fontsize=12)
plt.xticks(fontsize=11)
plt.yticks(fontsize=11)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('custom_conference_papers.png', dpi=300, bbox_inches='tight')
plt.show()

# Display data
print("Customizable Paper Counts:")
print(df)