"""
Advanced statistical analysis engine for premium data insights.
"""
import pandas as pd
import numpy as np
from scipy import stats


def calculate_advanced_stats(df):
    """
    Calculate advanced statistical metrics for all numeric columns.
    
    Returns:
        dict: Statistical summary for each numeric column
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    statistical_summary = {}
    
    for col in numeric_cols:
        data = df[col].dropna()
        
        if len(data) > 0:
            statistical_summary[col] = {
                'mean': float(data.mean()),
                'median': float(data.median()),
                'std': float(data.std()),
                'var': float(data.var()),
                'min': float(data.min()),
                'max': float(data.max()),
                'range': float(data.max() - data.min()),
                'q1': float(data.quantile(0.25)),
                'q3': float(data.quantile(0.75)),
                'iqr': float(data.quantile(0.75) - data.quantile(0.25)),
                'skewness': float(stats.skew(data)),
                'kurtosis': float(stats.kurtosis(data)),
                'count': len(data),
                'missing': len(df) - len(data),
                'missing_pct': float((len(df) - len(data)) / len(df) * 100) if len(df) > 0 else 0,
            }
    
    return statistical_summary


def detect_outliers(df):
    """
    Detect outliers using IQR method.
    
    Returns:
        dict: Outlier information per column
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    outlier_info = {}
    
    for col in numeric_cols:
        data = df[col].dropna()
        
        if len(data) > 0:
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            
            outlier_info[col] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(data) * 100) if len(data) > 0 else 0,
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                'values': outliers.tolist() if len(outliers) <= 10 else outliers.head(10).tolist(),
            }
    
    return outlier_info


def correlate_columns(df):
    """
    Calculate correlation matrix and identify strong relationships.
    
    Returns:
        tuple: (correlation matrix, strong correlations list)
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    
    if len(numeric_cols) < 2:
        return None, []
    
    corr_matrix = df[numeric_cols].corr()
    
    # Find strong correlations (> 0.7 or < -0.7)
    strong_corrs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            corr_val = corr_matrix.iloc[i, j]
            if abs(corr_val) > 0.7:
                strong_corrs.append({
                    'var1': corr_matrix.columns[i],
                    'var2': corr_matrix.columns[j],
                    'correlation': float(corr_val),
                    'strength': 'Very Strong' if abs(corr_val) > 0.9 else 'Strong'
                })
    
    return corr_matrix, strong_corrs


def calculate_data_quality_metrics(df, cleaning_steps):
    """
    Calculate comprehensive data quality metrics.
    
    Returns:
        dict: Data quality metrics
    """
    total_records = len(df)
    total_cells = len(df) * len(df.columns)
    missing_cells = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    outliers_count = 0
    
    for col in numeric_cols:
        data = df[col].dropna()
        if len(data) > 0:
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers_count += len(data[(data < lower_bound) | (data > upper_bound)])
    
    completeness_pct = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
    
    # Calculate quality score (0-100)
    quality_score = (
        (completeness_pct * 0.4) +  # 40% completeness
        (max(0, (100 - (duplicate_rows / total_records * 100)) if total_records > 0 else 0) * 0.3) +  # 30% uniqueness
        (max(0, (100 - (outliers_count / total_records * 10)) if total_records > 0 else 0) * 0.3)  # 30% validity
    )
    
    return {
        'total_records': total_records,
        'total_columns': len(df.columns),
        'missing_filled': missing_cells,
        'duplicates_removed': duplicate_rows,
        'completeness_pct': completeness_pct,
        'outliers_count': outliers_count,
        'quality_score': max(0, min(100, quality_score)),
    }


def generate_contextual_insights(df, statistical_summary, outlier_info, strong_corrs, mode="general"):
    """
    Generate crisp, actionable insights with specific observations.
    Avoids academic language, math notation, and generic statements.
    
    Args:
        df: DataFrame
        statistical_summary: Statistical metrics dictionary
        outlier_info: Outlier detection results
        strong_corrs: Strong correlations list
        mode: Domain mode (general, health, agri)
    
    Returns:
        list: List of formatted insight bullets
    """
    insights = []
    
    # 1. DISTRIBUTION PATTERNS (not academic)
    for col, stats_dict in list(statistical_summary.items())[:3]:
        skew = stats_dict['skewness']
        obs_count = stats_dict['count']
        
        # Only report if meaningful
        if abs(skew) > 0.8:
            direction = "skewed right" if skew > 0 else "skewed left"
            insights.append(f"'{col}' is {direction} → check for edge cases in {direction} tail")
    
    # 2. OUTLIERS WITH ACTION
    outlier_total = 0
    for col, outlier_dict in outlier_info.items():
        if outlier_dict['count'] > 0:
            outlier_total += outlier_dict['count']
            pct = outlier_dict['percentage']
            if pct > 3:  # Only flag significant outliers
                insights.append(f"{outlier_dict['count']} outliers in '{col}' ({pct:.1f}%) → validate before modeling")
    
    # 3. CORRELATIONS WITH CONTEXT
    if strong_corrs:
        for corr in strong_corrs[:2]:  # Top 2 only
            direction = "move together" if corr['correlation'] > 0 else "move opposite"
            strength = "very strong" if abs(corr['correlation']) > 0.9 else "strong"
            insights.append(
                f"'{corr['var1']}' & '{corr['var2']}' {direction} ({strength}) → "
                f"may represent same underlying factor"
            )
    
    # 4. DATA INTEGRITY
    missing_total = sum([s['missing'] for s in statistical_summary.values()])
    if missing_total > 0:
        insights.append(f"Filled {missing_total} missing values → review imputation assumptions")
    
    # 5. DOMAIN-SPECIFIC
    if mode == "health":
        insights.append("Health data: Flag any unexplained spikes in measurements → verify data collection")
    elif mode == "agri":
        insights.append("Agricultural data: Check seasonal patterns → may need temporal adjustments")
    elif mode == "general":
        # Generic insight
        if len(statistical_summary) > 2:
            insights.append("Multiple variables detected → check for multi-collinearity in models")
    
    # Ensure we always have specific insights, not generic fallback
    if len(insights) < 3:
        # Add data consistency observation
        completeness = ((len(df) * len(df.columns) - sum([s['missing'] for s in statistical_summary.values()])) 
                       / (len(df) * len(df.columns)) * 100)
        insights.append(f"Data completeness: {completeness:.0f}% → suitable for analysis")
    
    return insights
