import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

from utils.llm_client import generate
from tools.report_tool import generate_pdf_report
from utils.stats_engine import (
    calculate_advanced_stats,
    detect_outliers,
    correlate_columns,
    calculate_data_quality_metrics,
    generate_contextual_insights
)

# =========================
# PATHS
# =========================
CHART_DIR = "outputs/charts"
DATA_DIR = "data/cleaned"

os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Premium styling
sns.set_theme(style="whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10


# =========================
# CLEAN DATA
# =========================
def clean_data(df):
    steps = []

    missing = df.isnull().sum().sum()
    if missing > 0:
        df = df.fillna(df.median(numeric_only=True))
        steps.append(f"Filled {missing} missing values using median imputation")

    before = len(df)
    df = df.drop_duplicates()
    after = len(df)

    if before != after:
        steps.append(f"Removed {before - after} duplicate rows ({((before-after)/before*100):.1f}%)")

    return df, steps


# =========================
# ENHANCED CHARTS
# =========================
def create_histogram_enhanced(df, col, idx):
    """Create enhanced histogram with distribution curve and statistics."""
    path = os.path.join(CHART_DIR, f"hist_{idx}.png")
    
    fig, ax = plt.subplots(figsize=(9, 5))
    data = df[col].dropna()
    
    # Histogram with KDE
    sns.histplot(data, kde=True, stat="density", bins=30, ax=ax, 
                color='#2E86AB', edgecolor='white', linewidth=1.2)
    
    # Add mean and median lines
    mean_val = data.mean()
    median_val = data.median()
    
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
    ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
    
    ax.set_title(f"{col.replace('_', ' ').title()} Distribution", 
                fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel(col.replace('_', ' ').title(), fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    return path


def create_boxplot_enhanced(df, col, idx):
    """Create enhanced boxplot with outlier annotations."""
    path = os.path.join(CHART_DIR, f"box_{idx}.png")
    
    fig, ax = plt.subplots(figsize=(9, 5))
    data = df[col].dropna()
    
    # Boxplot
    bp = ax.boxplot(data, vert=True, patch_artist=True, widths=0.5,
                   boxprops=dict(facecolor='#A23B72', alpha=0.7),
                   medianprops=dict(color='red', linewidth=2),
                   whiskerprops=dict(color='#333333', linewidth=1.5),
                   capprops=dict(color='#333333', linewidth=1.5))
    
    # Calculate outliers
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = data[(data < lower) | (data > upper)]
    
    # Plot outliers
    if len(outliers) > 0:
        ax.scatter([1]*len(outliers), outliers, color='red', s=100, zorder=3, 
                  marker='o', edgecolor='darkred', linewidth=1.5, label=f'Outliers ({len(outliers)})')
    
    ax.set_title(f"{col.replace('_', ' ').title()} - Outlier Analysis", 
                fontsize=13, fontweight='bold', pad=15)
    ax.set_ylabel(col.replace('_', ' ').title(), fontsize=11)
    ax.set_xticklabels([col.replace('_', ' ').title()])
    if len(outliers) > 0:
        ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    return path


def create_correlation_heatmap(df):
    """Create enhanced correlation heatmap with annotations."""
    path = os.path.join(CHART_DIR, "correlation_heatmap.png")
    
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    
    if len(numeric_cols) < 2:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 8))
    corr = df[numeric_cols].corr()
    
    # Create heatmap with better styling
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
               cbar_kws={'label': 'Correlation Coefficient'},
               annot_kws={'size': 9}, linewidths=0.5, linecolor='white',
               vmin=-1, vmax=1, ax=ax, square=True)
    
    ax.set_title("Correlation Matrix Heatmap", fontsize=13, fontweight='bold', pad=15)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    return path


def create_distribution_comparison(df):
    """Create multi-subplot distribution comparison for all numeric columns."""
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    
    if len(numeric_cols) == 0:
        return None
    
    # Limit to 6 columns for readability
    cols_to_plot = numeric_cols[:6]
    n_cols = min(3, len(cols_to_plot))
    n_rows = (len(cols_to_plot) + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 4*n_rows))
    axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]
    
    for idx, col in enumerate(cols_to_plot):
        ax = axes[idx]
        data = df[col].dropna()
        
        sns.histplot(data, kde=True, ax=ax, color='#2E86AB', edgecolor='white', linewidth=1)
        ax.set_title(f"{col.replace('_', ' ').title()}", fontweight='bold')
        ax.set_xlabel('')
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for idx in range(len(cols_to_plot), len(axes)):
        axes[idx].set_visible(False)
    
    plt.suptitle("Distribution Analysis - All Numeric Columns", 
                fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    path = os.path.join(CHART_DIR, "distribution_comparison.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    return path


def create_summary_statistics_chart(statistical_summary):
    """Create a visual summary of key statistical metrics."""
    path = os.path.join(CHART_DIR, "statistics_summary.png")
    
    cols_to_show = list(statistical_summary.keys())[:4]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()
    
    for idx, col in enumerate(cols_to_show):
        ax = axes[idx]
        stats_dict = statistical_summary[col]
        
        # Create a simple stats display
        metrics = ['Mean', 'Median', 'Std Dev', 'Min', 'Max']
        values = [
            stats_dict['mean'],
            stats_dict['median'],
            stats_dict['std'],
            stats_dict['min'],
            stats_dict['max']
        ]
        
        colors_bar = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
        bars = ax.barh(metrics, values, color=colors_bar)
        
        ax.set_title(f"{col.replace('_', ' ').title()}", fontweight='bold', fontsize=11)
        ax.set_xlabel('Value')
        
        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'{width:.2f}', ha='left', va='center', fontsize=9)
    
    # Hide unused subplots
    for idx in range(len(cols_to_show), 4):
        axes[idx].set_visible(False)
    
    plt.suptitle("Statistical Metrics Summary", fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    return path


# =========================
# MAIN ANALYSIS ENGINE
# =========================
def analyze_excel_with_ai(file_path, model, mode, chart_type, user_input):
    """
    Premium data analysis pipeline with advanced analytics and reporting.
    
    Args:
        file_path: Path to data file (XLSX or CSV)
        model: LLM model to use
        mode: Analysis mode (general, health, agri)
        chart_type: Chart type preference (auto, histogram, boxplot, heatmap)
        user_input: User's specific question/focus
    
    Returns:
        dict: Analysis results with status, insights, report path, etc.
    """
    try:
        # Load data
        df = pd.read_excel(file_path) if file_path.endswith("xlsx") else pd.read_csv(file_path)
        
        # STEP 1: DATA CLEANING
        df, cleaning_steps = clean_data(df)
        
        clean_path = os.path.join(DATA_DIR, "cleaned_data.csv")
        df.to_csv(clean_path, index=False)
        
        # STEP 2: ADVANCED STATISTICAL ANALYSIS
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        
        # Calculate comprehensive statistics
        statistical_summary = calculate_advanced_stats(df)
        
        # Detect outliers
        outlier_info = detect_outliers(df)
        
        # Correlation analysis
        corr_matrix, strong_corrs = correlate_columns(df)
        
        # Data quality metrics
        data_quality_metrics = calculate_data_quality_metrics(df, cleaning_steps)
        
        # STEP 3: CHART GENERATION
        chart_paths = []
        chart_insights = []
        
        # Create enhanced charts for top numeric columns
        for i, col in enumerate(numeric_cols[:4]):
            # Histogram
            hist_path = create_histogram_enhanced(df, col, i)
            chart_paths.append(hist_path)
            
            stats_dict = statistical_summary[col]
            hist_insight = (f"Distribution of {col}: Mean={stats_dict['mean']:.2f}, "
                          f"Median={stats_dict['median']:.2f}, "
                          f"Std={stats_dict['std']:.2f}")
            chart_insights.append(hist_insight)
            
            # Boxplot
            box_path = create_boxplot_enhanced(df, col, i)
            chart_paths.append(box_path)
            
            outlier_count = outlier_info[col]['count']
            box_insight = (f"Outlier analysis for {col}: {outlier_count} outliers detected "
                         f"({outlier_info[col]['percentage']:.1f}% of data)")
            chart_insights.append(box_insight)
        
        # Add distribution comparison
        dist_path = create_distribution_comparison(df)
        if dist_path:
            chart_paths.append(dist_path)
            chart_insights.append("Comparative distribution patterns across numeric columns reveal data consistency.")
        
        # Add statistics summary chart
        stats_chart_path = create_summary_statistics_chart(statistical_summary)
        if stats_chart_path:
            chart_paths.append(stats_chart_path)
            chart_insights.append("Summary of key statistical metrics (mean, median, std dev, min, max) for major columns.")
        
        # Correlation heatmap
        if len(numeric_cols) > 1:
            corr_path = create_correlation_heatmap(df)
            if corr_path:
                chart_paths.append(corr_path)
                
                if strong_corrs:
                    corr_insight = f"Strong correlations identified: {len(strong_corrs)} relationship(s) detected between variables."
                else:
                    corr_insight = "Correlation analysis shows variables are relatively independent."
                chart_insights.append(corr_insight)
        
        # STEP 4: AI-POWERED INSIGHTS (ENHANCED, CONCISE)
        # Get contextual insights (returns list now)
        contextual_insights = generate_contextual_insights(
            df, statistical_summary, outlier_info, strong_corrs, mode
        )
        
        # Enhanced prompt for LLM - request clear, actionable insights
        summary = df.describe().to_string()
        
        prompt = f"""You are a senior data analyst. Provide CRISP, ACTIONABLE insights.

RULES:
• Maximum 8 insights
• 1 insight per line, start with •
• No math notation (ρ, σ, etc.)
• No academic jargon
• Use arrow notation: → for implications
• Be specific with numbers
• Format: "[emoji] observation → action/implication"

EXAMPLES:
• Strong ID-YEAR correlation → records are time-linked
• 8 outliers in BEAT field → validate before modeling
• DISTRICT consistency: 95% → good for geographic analysis

DATASET:
{summary}

Focus on {mode} context."""

        llm_insights_text = generate(prompt, model=model)
        
        # Parse LLM response into clean list
        llm_insights = [line.strip() for line in llm_insights_text.split('\n') 
                       if line.strip() and not line.startswith('Example')]
        
        # Combine insights: contextual + LLM (limit to 7 total)
        all_insights = contextual_insights + llm_insights
        final_insights = all_insights[:7]  # Take top 7
        insights_text = "\n".join(final_insights)

        # STEP 6: GENERATE PREMIUM PDF REPORT
        report_path = generate_pdf_report(
            insights=final_insights,  # Pass list for report layout
            cleaning_steps=cleaning_steps,
            chart_paths=chart_paths,
            chart_insights=chart_insights,
            data_summary=df.describe(),
            data_quality_metrics=data_quality_metrics,
            statistical_summary=statistical_summary
        )

        return {
            "status": "success",
            "insights": insights_text,
            "report_insights": final_insights,
            "analysis": df.describe().to_dict(),
            "report": report_path,
            "cleaned_file": clean_path,
            "statistics": statistical_summary,
            "quality_metrics": data_quality_metrics,
            "charts_generated": len(chart_paths),
            "strong_correlations": strong_corrs,
            "outliers_detected": sum(info['count'] for info in outlier_info.values())
        }
    
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }