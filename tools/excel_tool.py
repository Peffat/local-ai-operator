import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import re
from utils.llm_client import generate
from tools.report_tool import generate_pdf_report
from utils.stats_engine import calculate_advanced_stats, detect_outliers, correlate_columns, calculate_data_quality_metrics, generate_contextual_insights

CHART_DIR = "outputs/charts"
DATA_DIR = "data/cleaned"
os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'


# ═══════════════════════════════════════════════════════════════════
# STEP 1: LOAD & CLEAN DATA
# ═══════════════════════════════════════════════════════════════════
def load_and_clean(file_path):
    """Load CSV or XLSX and perform basic cleaning."""
    if file_path.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
    
    df.columns = df.columns.astype(str)
    
    # Fill missing values
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown')
    
    # Remove exact duplicates
    df = df.drop_duplicates()
    
    return df


# ═══════════════════════════════════════════════════════════════════
# STEP 2: UNDERSTAND SCHEMA
# ═══════════════════════════════════════════════════════════════════
def get_schema_audit(df):
    """Get column types, uniqueness, samples for LLM audit."""
    audit = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        unique = df[col].nunique()
        samples = df[col].dropna().unique()[:3]
        is_likely_id = (dtype in ['int64', 'float64'] and unique == len(df) and 
                       any(kw in col.lower() for kw in ['id', 'index', 'serial', 'no', 'num', 'sno', 'key']))
        audit.append({
            'column': col,
            'type': dtype,
            'unique': unique,
            'samples': list(samples),
            'is_likely_id': is_likely_id
        })
    return audit


def infer_target_column(df):
    """Infer which column is the target/outcome."""
    numeric = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    target_patterns = ['final_exam_score', 'pass_fail', 'grade_category', 'score', 'result', 'outcome', 'performance', 'target']

    for pattern in target_patterns:
        for col in df.columns:
            if pattern in col.lower():
                return col

    if 'final_exam_score' in df.columns:
        return 'final_exam_score'

    if len(numeric) > 0:
        return numeric[0]

    return df.columns[0]


def summarize_dataset_audit(audit_list, df, target_col):
    """Create a concise dataset overview that explains structure and risks."""
    numeric_cols = [item['column'] for item in audit_list if item['type'] in ['int64', 'float64', 'int32', 'float32']]
    categorical_cols = [item['column'] for item in audit_list if item['column'] not in numeric_cols]
    missing_columns = [item['column'] for item in audit_list if df[item['column']].isna().sum() > 0]
    high_cardinality = [col for col in categorical_cols if df[col].nunique() > 20]

    lines = [
        f"Dataset contains {len(df)} records and {len(df.columns)} columns.",
        f"Numeric columns: {', '.join(numeric_cols[:8]) or 'None'}.",
        f"Categorical columns: {', '.join(categorical_cols[:8]) or 'None'}.",
        f"Target column selected: {target_col}.",
    ]
    if missing_columns:
        lines.append(f"Missing values are present in {', '.join(missing_columns[:4])}.")
    if high_cardinality:
        lines.append(f"High-cardinality categorical variables include {', '.join(high_cardinality[:3])}.")
    return ' '.join(lines)


# ═══════════════════════════════════════════════════════════════════
# STEP 3: LLM AUDIT (Phase 1)
# ═══════════════════════════════════════════════════════════════════
def get_llm_audit(df, audit_list, model, target_col):
    """Ask LLM to audit the schema and provide a polished data overview."""
    audit_text = ""
    for item in audit_list:
        if not item['is_likely_id']:
            audit_text += f"- {item['column']}: {item['type']}, unique_values={item['unique']}.\n"

    summary_hint = summarize_dataset_audit(audit_list, df, target_col)
    prompt = f"""You are a senior data analyst reviewing a student performance dataset.

{summary_hint}

COLUMNS:
{audit_text}

Please provide a short executive overview in 2-3 sentences that covers:
- what this dataset is about
- the likely target and strongest candidate predictors
- any data quality or distribution signals to watch

Do not list raw column data or technical details. Keep it professional and narrative."""

    llm_output = generate(prompt, model=model)
    if not llm_output or llm_output.startswith("LLM Error:"):
        return summary_hint

    return llm_output.strip()


# ═══════════════════════════════════════════════════════════════════
# STEP 4: ANALYZE DATA
# ═══════════════════════════════════════════════════════════════════
def analyze_data(df, target_col):
    """Calculate stats, correlations, outliers, and quality signals."""
    numeric = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Remove ID-like columns from analysis
    numeric = [c for c in numeric if not any(kw in c.lower() for kw in ['id', 'index', 'serial', 'key', 'no', 'num'])]
    categorical = [c for c in categorical if not any(kw in c.lower() for kw in ['id', 'index', 'serial', 'key'])]

    numeric_df = df[numeric] if numeric else pd.DataFrame()
    stats = calculate_advanced_stats(numeric_df) if not numeric_df.empty else {}
    outliers = detect_outliers(numeric_df) if not numeric_df.empty else {}
    corr_matrix, strong_corrs = correlate_columns(numeric_df) if not numeric_df.empty else (None, [])

    missing_summary = df.isna().sum().to_dict()
    unique_counts = {col: int(df[col].nunique()) for col in df.columns}

    return {
        'numeric': numeric,
        'categorical': categorical,
        'stats': stats,
        'outliers': outliers,
        'correlations': strong_corrs,
        'missing': missing_summary,
        'unique_counts': unique_counts,
        'target': target_col
    }


# ═══════════════════════════════════════════════════════════════════
# STEP 5: LLM GENERATES INSIGHTS (Phase 2-4)
# ═══════════════════════════════════════════════════════════════════
def get_llm_insights(df, analysis, target_col, model):
    """Ask LLM to generate richer insights and a story summary."""
    numeric = analysis['numeric'][:6]
    categorical = analysis['categorical'][:5]
    corr_summary = "\n".join([
        f"- {c['var1']} vs {c['var2']}: {c['correlation']:.2f} ({c['strength']})"
        for c in analysis['correlations'][:4]
    ]) or "- No very strong numeric correlations found."

    top_missing = [f"{col} ({count} missing)" for col, count in sorted(analysis['missing'].items(), key=lambda item: -item[1]) if count > 0][:4]
    missing_text = ", ".join(top_missing) if top_missing else "No missing values detected."

    top_unique = [
        f"{col} ({count} distinct)"
        for col, count in sorted(analysis['unique_counts'].items(), key=lambda item: -item[1])[:4]
    ]
    unique_text = ", ".join(top_unique) if top_unique else "No distinct-value summary available."

    target_corrs = []
    if target_col in df.select_dtypes(include=['int64', 'float64']).columns:
        corr_series = df.select_dtypes(include=['int64', 'float64']).corrwith(df[target_col]).drop(target_col, errors='ignore').abs().sort_values(ascending=False)
        target_corrs = [f"{col} ({corr_series[col]:.2f})" for col in corr_series.index[:4]]
    target_corrs_text = ", ".join(target_corrs) if target_corrs else "No strong numeric predictors identified yet."

    prompt = f"""You are a premium data analyst. Analyze the dataset and produce a deep, structured report for a data analyst.

DATASET: {len(df)} records
TARGET: {target_col}
NUMERIC VARIABLES: {', '.join(numeric) if numeric else 'None'}
CATEGORICAL VARIABLES: {', '.join(categorical) if categorical else 'None'}
MISSING VALUE SUMMARY: {missing_text}
TOP DISTINCT COUNTS: {unique_text}
TOP TARGET CORRELATIONS: {target_corrs_text}
TOP CORRELATION PAIRS:
{corr_summary}

Write 6 premium insights. Each insight must be exactly one line formatted as:
Insight Title: [brief headline]. Description: [key finding and logic]. Action: [next step for analysis or business]. Chart: [bar/scatter/histogram/boxplot]

Use at least two insights to explain correlations, one insight to explain data quality or distribution risk, and one insight to explain a strong predictor or segment pattern.

Then add a STORY SUMMARY section with one short paragraph that links the findings into a clear narrative, explains why they matter, and identifies the most important data relationships.

Use the exact column names provided above. Do not use generic phrases. Focus on data relationships, quality signals, practical actions, and analyst logic."""

    llm_output = generate(prompt, model=model)
    if not llm_output or llm_output.startswith("LLM Error:"):
        fallback_insights = generate_contextual_insights(
            df,
            analysis['stats'],
            analysis['outliers'],
            analysis['correlations'],
            mode="general"
        )
        fallback_text = "\n".join([
            f"Insight Title: {insight}. Description: General signal found. Action: Review data. Chart: bar"
            for insight in fallback_insights[:6]
        ])
        fallback_story = "STORY SUMMARY: The dataset shows important distribution and correlation patterns that should be validated before modeling."
        return fallback_text + "\n\n" + fallback_story

    return llm_output


# ═══════════════════════════════════════════════════════════════════
# STEP 6: CREATE CHARTS
# ═══════════════════════════════════════════════════════════════════
def create_distribution_chart(df, col, idx):
    """Distribution of a numeric column."""
    path = os.path.join(CHART_DIR, f"dist_{idx}.png")
    fig, ax = plt.subplots(figsize=(7, 4))
    data = df[col].dropna()
    
    sns.histplot(data, kde=True, stat="density", bins=25, ax=ax, color='#2E86AB', edgecolor='white')
    ax.axvline(data.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {data.mean():.2f}')
    
    ax.set_title(f"{col.title()} Distribution", fontsize=12, fontweight='bold')
    ax.set_xlabel(col.title(), fontsize=10)
    ax.set_ylabel("Density", fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()
    return path


def create_scatter_chart(df, col1, col2, idx):
    """Scatter plot of relationship between two numeric columns."""
    path = os.path.join(CHART_DIR, f"scatter_{idx}.png")
    fig, ax = plt.subplots(figsize=(7, 4))
    data = df[[col1, col2]].dropna()
    
    sns.scatterplot(data=data, x=col1, y=col2, ax=ax, alpha=0.6, s=50, color='#2E86AB')
    if len(data) > 10:
        sns.regplot(data=data, x=col1, y=col2, ax=ax, scatter=False, color='red', line_kws={'linewidth': 2})
    
    ax.set_title(f"{col1.title()} vs {col2.title()}", fontsize=12, fontweight='bold')
    ax.set_xlabel(col1.title(), fontsize=10)
    ax.set_ylabel(col2.title(), fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()
    return path


def create_category_chart(df, cat_col, num_col, idx):
    """Bar chart of numeric across categories."""
    path = os.path.join(CHART_DIR, f"category_{idx}.png")
    fig, ax = plt.subplots(figsize=(8, 4))
    
    grouped = df.groupby(cat_col)[num_col].mean().sort_values(ascending=False).head(8)
    colors = sns.color_palette("husl", len(grouped))
    bars = ax.bar(range(len(grouped)), grouped.values, color=colors, alpha=0.8)
    
    ax.set_title(f"Average {num_col.title()} by {cat_col.title()}", fontsize=12, fontweight='bold')
    ax.set_xlabel(cat_col.title(), fontsize=10)
    ax.set_ylabel(f"Average {num_col.title()}", fontsize=10)
    ax.set_xticks(range(len(grouped)))
    ax.set_xticklabels(grouped.index, rotation=45, ha='right', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()
    return path


def create_boxplot_chart(df, cat_col, num_col, idx):
    """Boxplot of numeric values across categories."""
    path = os.path.join(CHART_DIR, f"boxplot_{idx}.png")
    fig, ax = plt.subplots(figsize=(8, 4))
    top_categories = df[cat_col].value_counts().nlargest(8).index.tolist()
    plot_df = df[df[cat_col].isin(top_categories)]
    sns.boxplot(data=plot_df, x=cat_col, y=num_col, ax=ax, palette='husl')
    ax.set_title(f"{num_col.title()} distribution by {cat_col.title()}", fontsize=12, fontweight='bold')
    ax.set_xlabel(cat_col.title(), fontsize=10)
    ax.set_ylabel(num_col.title(), fontsize=10)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()
    return path


def find_columns_in_text(text, candidate_columns):
    """Find candidate column names referenced in insight text."""
    found = []
    lower_text = text.lower()
    for col in sorted(candidate_columns, key=lambda c: -len(c)):
        col_key = col.lower()
        if col_key in lower_text or col_key.replace('_', ' ') in lower_text:
            found.append(col)
    return found


# ═══════════════════════════════════════════════════════════════════
# STEP 7: PARSE INSIGHTS & ASSIGN CHARTS
# ═══════════════════════════════════════════════════════════

def parse_insights(llm_output):
    """Parse LLM output into structured insights."""
    insights = []
    lines = [re.sub(r'^[\-\*\u2022]+\s*', '', l.strip())
             for l in llm_output.split('\n')
             if l.strip() and re.search(r'(Insight Title|Title|Key Finding)\s*:', l, re.IGNORECASE)]

    for line in lines[:6]:
        title = ''
        description = ''
        action = 'Review findings'
        chart_type = 'bar'

        title_match = re.search(r'(?:Insight Title|Title|Key Finding)\s*:\s*(.*?)(?:Description\s*:|Action\s*:|Chart\s*:|$)', line, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip().rstrip('.')

        desc_match = re.search(r'Description\s*:\s*(.*?)(?:Action\s*:|Chart\s*:|$)', line, re.IGNORECASE)
        if desc_match:
            description = desc_match.group(1).strip().rstrip('.')

        action_match = re.search(r'Action\s*:\s*(.*?)(?:Chart\s*:|$)', line, re.IGNORECASE)
        if action_match:
            action = action_match.group(1).strip().rstrip('.')

        chart_match = re.search(r'Chart\s*:\s*(\w+)', line, re.IGNORECASE)
        if chart_match:
            chart_type = chart_match.group(1).strip().lower()

        if not title:
            title = line.split('Action:')[0].strip().rstrip('.')
        if not description:
            description = line.split('Action:')[0].replace(title, '').strip().lstrip(':').strip()
        if not description:
            description = title

        title = title[:70]
        description = description[:240]

        insights.append({
            'title': title,
            'description': description,
            'action': action[:100],
            'chart_type': chart_type
        })

    if not insights:
        insights.append({
            'title': 'Key Finding',
            'description': 'Analysis complete with limited detail.',
            'action': 'Review the generated report for full context.',
            'chart_type': 'bar'
        })

    return insights


# ═══════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════
def analyze_excel_with_ai(file_path, model, mode, chart_type, user_input, progress_callback=None):
    """Clean, simple data analysis pipeline."""
    def update_status(message, percent=None):
        if progress_callback:
            try:
                progress_callback(message, percent)
            except Exception:
                pass

    try:
        update_status("[1/6] Loading data...", 5)
        print("[1/6] Loading data...")
        df = load_and_clean(file_path)
        clean_path = os.path.join(DATA_DIR, "cleaned_data.csv")
        df.to_csv(clean_path, index=False)
        
        update_status("[2/6] Auditing schema...", 15)
        print("[2/6] Auditing schema...")
        audit = get_schema_audit(df)
        target = infer_target_column(df)
        
        update_status("[3/6] Getting LLM audit...", 30)
        print("[3/6] Getting LLM audit...")
        llm_audit = get_llm_audit(df, audit, model, target)
        
        update_status("[4/6] Analyzing data...", 45)
        print("[4/6] Analyzing data...")
        analysis = analyze_data(df, target)
        quality_metrics = calculate_data_quality_metrics(df, [])
        
        update_status("[5/6] Getting LLM insights...", 60)
        print("[5/6] Getting LLM insights...")
        llm_insights_text = get_llm_insights(df, analysis, target, model)
        story_summary = ""
        if "STORY SUMMARY:" in llm_insights_text:
            story_summary = llm_insights_text.split("STORY SUMMARY:", 1)[1].strip()
            llm_insights_text = llm_insights_text.split("STORY SUMMARY:", 1)[0].strip()
        insights = parse_insights(llm_insights_text)

        update_status("[6/6] Creating charts...", 75)
        print("[6/6] Creating charts...")
        charts = []
        numeric = analysis['numeric']
        categorical = analysis['categorical']
        all_columns = df.columns.tolist()

        for idx, insight in enumerate(insights[:4]):
            chart_path = None
            chart_caption = insight['title']
            chart_type = insight.get('chart_type', 'bar')
            insight_text = f"{insight['title']} {insight.get('description', '')}"
            cols = find_columns_in_text(insight_text, all_columns)
            update_status(f"Creating chart {idx+1} of {min(len(insights), 4)}...", 75 + int((idx + 1) * 5))
            numeric_cols = [c for c in cols if c in numeric]
            categorical_cols = [c for c in cols if c in categorical]

            if chart_type == 'scatter' and len(numeric_cols) >= 2:
                chart_path = create_scatter_chart(df, numeric_cols[0], numeric_cols[1], idx)
            elif chart_type == 'boxplot' and categorical_cols and numeric_cols:
                chart_path = create_boxplot_chart(df, categorical_cols[0], numeric_cols[0], idx)
            elif chart_type == 'bar' and categorical_cols and numeric_cols:
                chart_path = create_category_chart(df, categorical_cols[0], numeric_cols[0], idx)
            elif chart_type in ['histogram', 'distribution'] and numeric_cols:
                chart_path = create_distribution_chart(df, numeric_cols[0], idx)

            if not chart_path:
                if idx == 0 and numeric:
                    chart_path = create_distribution_chart(df, target if target in numeric else numeric[0], idx)
                    chart_caption = f'Distribution of {target if target in numeric else numeric[0]}'
                elif len(analysis['correlations']) > 0:
                    corr = analysis['correlations'][0]
                    chart_path = create_scatter_chart(df, corr['var1'], corr['var2'], idx)
                    chart_caption = f'{corr["var1"]} vs {corr["var2"]} relationship'
                elif categorical and numeric:
                    chart_path = create_category_chart(df, categorical[0], numeric[0], idx)
                    chart_caption = f'Average {numeric[0]} by {categorical[0]}'

            if chart_path:
                charts.append({
                    'path': chart_path,
                    'type': chart_type,
                    'caption': chart_caption
                })

        if len(charts) < 3 and categorical and numeric:
            chart_path = create_category_chart(df, categorical[0], numeric[0], len(charts))
            charts.append({
                'path': chart_path,
                'type': 'category',
                'caption': f'Average {numeric[0]} by {categorical[0]}'
            })

        if not charts and numeric:
            chart_path = create_distribution_chart(df, numeric[0], 0)
            charts.append({'path': chart_path, 'type': 'distribution', 'caption': f'Distribution of {numeric[0]}'})

        update_status("[7/7] Generating PDF report...", 90)
        print("[Report] Generating PDF...")
        insights_text = "\n".join([f"• {i['title']} | {i['description']} | Action: {i['action']}" for i in insights])

        report_path = generate_pdf_report(
            insights=[f"{i['title']} | {i['description']} | Action: {i['action']}" for i in insights],
            cleaning_steps=[f"Processed {len(df)} records", "Filled missing values", "Removed duplicates"],
            chart_paths=[c['path'] for c in charts],
            chart_insights=[c.get('caption', '') for c in charts],
            data_summary=df.describe(),
            data_quality_metrics=quality_metrics,
            statistical_summary=analysis['stats'],
            skipped_columns=[],
            story_charts=[{
                'story_index': j,
                'path': charts[j]['path'],
                'type': charts[j]['type'],
                'caption': charts[j].get('caption', '')
            } for j in range(min(len(charts), len(insights)))],
            data_understanding=llm_audit,
            initial_insights=story_summary or "Data analyzed for patterns and relationships.",
            analysis_suggestions="The report includes key findings, chart evidence, and recommended next steps.",
            premium_story=story_summary or None
        )
        
        return {
            "status": "success",
            "insights": insights_text,
            "report_insights": insights,
            "report": report_path,
            "cleaned_file": clean_path,
            "charts_generated": len(charts),
            "strong_correlations": analysis['correlations'],
            "outliers_detected": sum(v['count'] for v in analysis['outliers'].values()) if analysis['outliers'] else 0
        }
    
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
