"""
Day 9: Exploratory Data Analysis (EDA)
Intern: Shri Sanjaykumar V | Role: AI/ML Intern | Organization: Linkific
Verified Environment: Python 3.14.3 | Pandas 3.0.3 | NumPy 2.5.0 | Matplotlib 3.11.0 | Seaborn 0.13.2

Description:
Automated Exploratory Data Analysis script for analyzing dataset structure, descriptive statistics,
distributions, category relationships, and temporal trends.
"""

import os
import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'axes.edgecolor': '#cccccc',
    'axes.linewidth': 0.8
})

def find_cleaned_dataset():
    candidates = [
        os.path.join("..", "Day-8", "cleaned_dataset.csv"),
        os.path.join(".", "cleaned_dataset.csv"),
        os.path.join(".", "Day-8", "cleaned_dataset.csv"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Day-8", "cleaned_dataset.csv"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleaned_dataset.csv")
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    raise FileNotFoundError("Could not locate cleaned_dataset.csv.")

def main():
    print("=" * 70)
    print("[EXPLORATORY DATA ANALYSIS STARTED]")
    print("=" * 70)

    dataset_path = find_cleaned_dataset()
    print(f"Dataset Located: {dataset_path}")
    df = pd.read_csv(dataset_path)

    # 1. Dataset Profile
    n_rows, n_cols = df.shape
    mem_usage = df.memory_usage(deep=True).sum() / 1024
    print(f"Dataset Shape: {n_rows:,} rows, {n_cols} columns")
    print(f"Memory Usage:  {mem_usage:.2f} KB")

    # 2. Feature Type Detection
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()

    date_cols = []
    for col in cat_cols.copy():
        if 'id' in col.lower():
            continue
        if any(term in col.lower() for term in ['date', 'time', 'year']):
            sample = df[col].dropna().head(50)
            try:
                converted = pd.to_datetime(sample, format='mixed', errors='coerce')
                if converted.notna().sum() > (0.8 * len(sample)):
                    date_cols.append(col)
                    cat_cols.remove(col)
            except Exception:
                pass

    for col in num_cols.copy():
        if 'id' in col.lower():
            num_cols.remove(col)

    continuous_num_cols = [c for c in num_cols if df[c].nunique() > 20]
    print(f"Numerical Features:   {num_cols}")
    print(f"Categorical Features: {cat_cols}")
    print(f"Temporal Features:    {date_cols}")

    # Output directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    charts_dir = os.path.join(script_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # 3. Visualization 1: Category Distribution
    cat1_col = next((c for c in cat_cols if 'dept' in c.lower() or 'department' in c.lower()), None)
    if not cat1_col and cat_cols:
        cat1_col = next((c for c in cat_cols if 4 <= df[c].nunique() <= 35), cat_cols[0])

    cat1_counts = df[cat1_col].value_counts()
    plt.figure(figsize=(12, 8))
    ax1 = sns.barplot(x=cat1_counts.values, y=cat1_counts.index, hue=cat1_counts.index, palette="Blues_r", legend=False)
    for p in ax1.patches:
        w = p.get_width()
        pct = (w / len(df)) * 100
        ax1.annotate(f" {int(w):,} ({pct:.1f}%)", (w, p.get_y() + p.get_height() / 2.),
                     va='center', ha='left', fontsize=9, color='#111111')
    plt.title(f"{cat1_col.capitalize()} Distribution (Total: {len(df):,} Records)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Records", fontsize=11, labelpad=8)
    plt.ylabel(cat1_col.capitalize(), fontsize=11, labelpad=8)
    plt.xlim(0, max(cat1_counts.values) * 1.22)
    plt.tight_layout()
    v1_path = os.path.join(charts_dir, "1_category_distribution.png")
    plt.savefig(v1_path, dpi=300)
    plt.close()
    print(f"Chart 1 Saved: {v1_path}")

    # 4. Visualization 2: Numerical Comparison by Category
    num_col = continuous_num_cols[0] if continuous_num_cols else num_cols[0]
    avg_series = df.groupby(cat1_col)[num_col].mean().sort_values(ascending=False)

    plt.figure(figsize=(12, 9))
    ax2 = sns.barplot(x=avg_series.values, y=avg_series.index, hue=avg_series.index, palette="viridis", legend=False)
    for p in ax2.patches:
        w = p.get_width()
        prefix = "$" if "sal" in num_col.lower() else ""
        ax2.annotate(f" {prefix}{w:,.0f}", (w, p.get_y() + p.get_height() / 2.),
                     va='center', ha='left', fontsize=9, color='#111111')
    plt.title(f"Average {num_col.replace('_', ' ').title()} by {cat1_col.capitalize()}", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel(f"Average {num_col.replace('_', ' ').title()} ({prefix})", fontsize=11, labelpad=8)
    plt.ylabel(cat1_col.capitalize(), fontsize=11, labelpad=8)
    plt.xlim(0, max(avg_series.values) * 1.18)
    plt.tight_layout()
    v2_path = os.path.join(charts_dir, "2_numerical_comparison.png")
    plt.savefig(v2_path, dpi=300)
    plt.close()
    print(f"Chart 2 Saved: {v2_path}")

    # 5. Visualization 3: Numerical Distribution with Stats Callout Box
    plt.figure(figsize=(11, 6))
    mean_val = df[num_col].mean()
    median_val = df[num_col].median()
    std_val = df[num_col].std()
    skew_val = df[num_col].skew()
    prefix = "$" if "sal" in num_col.lower() else ""

    sns.histplot(df[num_col], kde=True, bins=30, color="#1f77b4", edgecolor="white", alpha=0.65)
    plt.axvline(mean_val, color="#d62728", linestyle="--", linewidth=2.2, label=f"Mean: {prefix}{mean_val:,.2f}")
    plt.axvline(median_val, color="#2ca02c", linestyle="-.", linewidth=2.2, label=f"Median: {prefix}{median_val:,.2f}")

    skew_text = "Right-Skewed" if skew_val > 0.2 else ("Left-Skewed" if skew_val < -0.2 else "Symmetric")
    stats_box = (
        f"Descriptive Statistics:\n"
        f"• Mean: {prefix}{mean_val:,.2f}\n"
        f"• Median: {prefix}{median_val:,.2f}\n"
        f"• Std Dev: {prefix}{std_val:,.2f}\n"
        f"• Skewness: {skew_val:+.2f} ({skew_text})"
    )
    plt.gca().text(
        0.72, 0.58, stats_box, transform=plt.gca().transAxes,
        fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.6', facecolor='#f8f9fa', edgecolor='#cccccc', alpha=0.95)
    )

    plt.title(f"{num_col.replace('_', ' ').title()} Distribution", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel(f"{num_col.replace('_', ' ').title()} ({prefix})", fontsize=11, labelpad=8)
    plt.ylabel("Frequency (Record Count)", fontsize=11, labelpad=8)
    plt.legend(frameon=True, loc="upper right", fontsize=10)
    plt.tight_layout()
    v3_path = os.path.join(charts_dir, "3_numerical_distribution.png")
    plt.savefig(v3_path, dpi=300)
    plt.close()
    print(f"Chart 3 Saved: {v3_path}")

    # 6. Visualization 4: Part-to-Whole Donut Chart with Side Legend
    pie_candidates = [c for c in cat_cols if c != cat1_col and 2 <= df[c].nunique() <= 7]
    pie_col = pie_candidates[0] if pie_candidates else (cat_cols[1] if len(cat_cols) > 1 else cat1_col)
    pie_counts = df[pie_col].value_counts()

    fig, ax = plt.subplots(figsize=(11, 6.5))
    colors = sns.color_palette("tab10")[0:len(pie_counts)]
    explode = [0.03 if i == 0 else 0 for i in range(len(pie_counts))]

    wedges, texts = ax.pie(
        pie_counts.values,
        explode=explode,
        colors=colors,
        startangle=140,
        wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2)
    )

    ax.text(0, 0, f"Total\n{len(df):,}\nRecords", ha='center', va='center', fontsize=12, fontweight='bold', color='#333333')

    legend_labels = [f"{idx}: {val:,} ({val/len(df)*100:.1f}%)" for idx, val in zip(pie_counts.index, pie_counts.values)]
    ax.legend(
        wedges, legend_labels,
        title=f"{pie_col.replace('_', ' ').title()}",
        title_fontsize=11,
        loc='center left',
        bbox_to_anchor=(1.02, 0.5),
        fontsize=10,
        frameon=True
    )

    ax.set_title(f"{pie_col.replace('_', ' ').title()} Distribution (Part-to-Whole)", fontsize=14, fontweight="bold", pad=15)
    v4_path = os.path.join(charts_dir, "4_part_to_whole.png")
    plt.savefig(v4_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Chart 4 Saved: {v4_path}")

    # 7. Visualization 5: Time Trend with Headroom and Callout Box
    date_col = next((c for c in date_cols if 'hire' in c.lower()), (date_cols[0] if date_cols else None))
    if date_col:
        parsed_dates = pd.to_datetime(df[date_col], errors="coerce")
        valid_years = parsed_dates.dt.year.dropna().astype(int).value_counts().sort_index()
        peak_yr = int(valid_years.idxmax())
        peak_cnt = int(valid_years.max())

        plt.figure(figsize=(12, 5.5))
        plt.plot(valid_years.index, valid_years.values, marker="o", markersize=5.5, color="#1b9e77", linewidth=2.4)
        plt.fill_between(valid_years.index, valid_years.values, color="#1b9e77", alpha=0.15)

        plt.ylim(0, peak_cnt * 1.25)
        plt.annotate(
            f"Peak Intake: {peak_cnt:,} hires ({peak_yr})",
            xy=(peak_yr, peak_cnt),
            xytext=(peak_yr - 10, peak_cnt + 14),
            arrowprops=dict(facecolor='#111111', shrink=0.08, width=1.5, headwidth=7),
            fontweight='bold', fontsize=10.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#ffffff", edgecolor="#1b9e77", linewidth=1.5)
        )

        plt.title(f"Yearly Hiring Trend Over Time ({date_col})", fontsize=14, fontweight="bold", pad=15)
        plt.xlabel("Hiring Year", fontsize=11, labelpad=8)
        plt.ylabel("Number of Employees Hired", fontsize=11, labelpad=8)
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        v5_path = os.path.join(charts_dir, "5_time_trend.png")
        plt.savefig(v5_path, dpi=300)
        plt.close()
        print(f"Chart 5 Saved: {v5_path}")

    # 8. 5 Business Insights
    top_cat1_name = cat1_counts.index[0]
    top_cat1_count = cat1_counts.iloc[0]
    top_cat1_pct = (top_cat1_count / len(df)) * 100
    insight_1_finding = f"Within the '{cat1_col}' dimension, '{top_cat1_name}' represents the largest single segment with {top_cat1_count:,} records, constituting {top_cat1_pct:.2f}% of the total analyzed dataset."
    insight_1_meaning = "Workforce planning and operational budgeting should account for the heavy staffing concentration in emergency and public safety operations."

    highest_cat = avg_series.index[0]
    highest_avg = avg_series.iloc[0]
    lowest_cat = avg_series.index[-1]
    lowest_avg = avg_series.iloc[-1]
    disparity_ratio = highest_avg / lowest_avg if lowest_avg > 0 else 0
    num_unit = "$" if "sal" in num_col.lower() else ""
    insight_2_finding = f"Average {num_col} varies significantly across {cat1_col} groups. The highest average is observed in '{highest_cat}' at {num_unit}{highest_avg:,.2f}, while the lowest average is in '{lowest_cat}' at {num_unit}{lowest_avg:,.2f}, representing a {disparity_ratio:.2f}x spread."
    insight_2_meaning = "Cross-department compensation benchmarks can inform compensation equity reviews and specialized talent acquisition strategies."

    skew_label = "positively skewed (right-skewed)" if skew_val > 0.2 else ("negatively skewed (left-skewed)" if skew_val < -0.2 else "approximately symmetric")
    insight_3_finding = f"The metric '{num_col}' exhibits an overall mean of {num_unit}{mean_val:,.2f} and a median of {num_unit}{median_val:,.2f} (standard deviation: {num_unit}{std_val:,.2f}, skewness: {skew_val:.2f}). Because the mean exceeds the median, the distribution is {skew_label}."
    insight_3_meaning = "For budgeting and typical compensation planning, median figures provide a more reliable benchmark than the arithmetic mean, which is elevated by high-earning leadership roles."

    top_pie_name = pie_counts.index[0]
    top_pie_count = pie_counts.iloc[0]
    top_pie_pct = (top_pie_count / len(df)) * 100
    insight_4_finding = f"In the '{pie_col}' breakdown, the primary classification is '{top_pie_name}', which comprises {top_pie_count:,} records ({top_pie_pct:.2f}% of all records)."
    insight_4_meaning = "Tracking demographic baselines enables human resources leadership to evaluate diversity, equity, and inclusion initiatives across operational divisions."

    min_yr = int(valid_years.index.min()) if date_col and not valid_years.empty else 0
    max_yr = int(valid_years.index.max()) if date_col and not valid_years.empty else 0
    insight_5_finding = f"Historical records spanning from {min_yr} to {max_yr} reveal that peak intake under '{date_col}' occurred in calendar year {peak_yr}, with {peak_cnt:,} records logged during that twelve-month interval."
    insight_5_meaning = "Identifying historical intake peaks assists talent acquisition in analyzing cohort retention and planning future recruitment campaigns."

    insights = [
        ("Insight 1: Category Volume Concentration", insight_1_finding, insight_1_meaning),
        ("Insight 2: Department Salary Disparity", insight_2_finding, insight_2_meaning),
        ("Insight 3: Central Tendency and Skewness", insight_3_finding, insight_3_meaning),
        ("Insight 4: Demographic Representation", insight_4_finding, insight_4_meaning),
        ("Insight 5: Longitudinal Hiring Trend", insight_5_finding, insight_5_meaning)
    ]

    print("\n" + "=" * 80)
    print("5 BUSINESS INSIGHTS DERIVED FROM DATASET METRICS")
    print("=" * 80)
    for title, finding, meaning in insights:
        print(f"\n{title}")
        print(f"  Finding:          {finding}")
        print(f"  Business Meaning: {meaning}")
        print("-" * 80)

    print("[EXPLORATORY DATA ANALYSIS EXECUTION COMPLETE]")

if __name__ == "__main__":
    main()
