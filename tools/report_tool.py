from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os

REPORT_DIR = "outputs/reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def generate_pdf_report(insights, cleaning_steps, chart_paths, chart_insights, 
                        data_summary=None, data_quality_metrics=None, statistical_summary=None):
    """
    Generate a premium PDF report with professional structure.
    Flow: Quality Dashboard → Key Insights → Visual Evidence → Stats → Recommendations
    
    Args:
        insights: List of key analytical insights (or string, will be converted)
        cleaning_steps: Data cleaning operations performed
        chart_paths: List of chart file paths
        chart_insights: List of insights for each chart
        data_summary: DataFrame summary statistics
        data_quality_metrics: Data quality metrics dictionary
        statistical_summary: Advanced statistical metrics dictionary
    """
    report_path = os.path.join(
        REPORT_DIR,
        f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.pdf"
    )
    doc = SimpleDocTemplate(report_path, topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.7*inch, rightMargin=0.7*inch)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=8,
        alignment=1
    )
    
    section_style = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#2e5c8a'),
        spaceAfter=8,
        spaceBefore=6,
        borderPadding=3
    )
    
    insight_style = ParagraphStyle(
        'InsightBullet',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=6,
        textColor=colors.HexColor('#1a1a1a')
    )
    
    elements = []
    
    # ====== COVER PAGE ======
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        "<b><font size=26>📊 AI-Powered Data Intelligence Report</font></b>",
        title_style
    ))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "<font size=9><i>Premium AI-Powered Analysis</i></font>",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 0.25*inch))
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"<b>Generated:</b> {timestamp}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Engine:</b> Gemma 4 (via Ollama)", styles["Normal"]))
    
    elements.append(Spacer(1, 0.25*inch))
    elements.append(PageBreak())
    
    # ====== EXECUTIVE SUMMARY ======
    elements.append(Paragraph("<b>📊 Executive Summary</b>", section_style))
    elements.append(Spacer(1, 8))
    
    # Generate dynamic executive summary based on data
    exec_summary_points = []
    
    if data_quality_metrics:
        records = data_quality_metrics.get('total_records', 0)
        quality_pct = data_quality_metrics.get('quality_score', 0)
        outliers = data_quality_metrics.get('outliers_count', 0)
        
        exec_summary_points.append(f"Dataset: {records:,} records, {'high' if quality_pct >= 90 else 'moderate'} quality ({quality_pct:.0f}%)")
        
        if outliers > 0:
            exec_summary_points.append(f"Key issue: {outliers:,} outliers detected across multiple features")
            exec_summary_points.append("Risk: outliers may distort modeling results")
            exec_summary_points.append("Recommendation: validate extreme values before analysis")
    
    # Add key insight from insights if available
    if insights:
        if isinstance(insights, str):
            insight_lines = insights.split("\n")
        else:
            insight_lines = insights
        
        # Take first meaningful insight
        for line in insight_lines[:3]:
            line = line.strip()
            if line and len(line) > 10:  # Meaningful length
                # Clean up the insight
                line = line.replace('•', '').strip()
                if not line.startswith('Key insight:'):
                    line = f"Key insight: {line}"
                exec_summary_points.append(line)
                break
    
    # Display executive summary points
    for point in exec_summary_points:
        elements.append(Paragraph(f"• {point}", insight_style))
    
    elements.append(Spacer(1, 12))
    elements.append(PageBreak())
    
    # ====== DATA QUALITY DASHBOARD ======
    if data_quality_metrics:
        elements.append(Paragraph("<b>📈 Data Quality</b>", section_style))
        elements.append(Spacer(1, 8))
        
        metrics_data = [
            ["Metric", "Value", "Status"],
            ["Records", str(data_quality_metrics.get('total_records', 'N/A')), "✓"],
            ["Completeness", f"{data_quality_metrics.get('completeness_pct', 0):.0f}%", 
             "✓" if data_quality_metrics.get('completeness_pct', 0) >= 95 else "⚠"],
            ["Duplicates Removed", str(data_quality_metrics.get('duplicates_removed', 0)), "✓"],
            ["Missing Values Filled", str(data_quality_metrics.get('missing_filled', 0)), "✓"],
            ["Outliers Detected", str(data_quality_metrics.get('outliers_count', 0)), "ℹ"],
            ["Quality Score", f"{data_quality_metrics.get('quality_score', 0):.0f}%", "✓"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 0.8*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 8))
    
    # ====== DATA CLEANING SUMMARY (compact) ======
    if cleaning_steps and len(cleaning_steps) > 0:
        elements.append(Paragraph("<b>🧹 Data Preparation</b>", section_style))
        elements.append(Spacer(1, 6))
        
        for step in cleaning_steps:
            elements.append(Paragraph(f"• {step}", styles["Normal"]))
        
        elements.append(Spacer(1, 8))
    
    elements.append(PageBreak())
    
    # ====== KEY INSIGHTS (NEW POSITION - RIGHT AFTER QUALITY) ======
    elements.append(Paragraph("<b>🔍 Key Insights</b>", section_style))
    elements.append(Spacer(1, 8))
    
    # Convert insights to list if string
    if isinstance(insights, str):
        insight_lines = insights.split("\n")
    else:
        insight_lines = insights
    
    # Display only first 7 insights, clean format
    for line in insight_lines[:7]:
        line = line.strip()
        if line and not line.startswith('•'):
            line = line.lstrip('- ')
        if line:
            # Remove excessive math notation and shorten
            line = line.replace('ρ', 'correlation').replace('σ', 'std dev')
            if len(line) > 100:
                line = line[:100] + "…"
            elements.append(Paragraph(f"• {line}", insight_style))
    
    elements.append(Spacer(1, 8))
    elements.append(PageBreak())
    
    # ====== VISUAL EVIDENCE (CHARTS) ======
    elements.append(Paragraph("<b>📈 Visual Evidence</b>", section_style))
    elements.append(Spacer(1, 10))
    
    for i, (chart, insight) in enumerate(zip(chart_paths, chart_insights)):
        if os.path.exists(chart):
            # Clean up chart caption
            caption = insight.strip()
            if len(caption) > 90:
                caption = caption[:87] + "…"
            
            elements.append(Paragraph(f"<b>Figure {i+1}:</b> {caption}", styles["Heading3"]))
            elements.append(Spacer(1, 6))
            
            elements.append(Image(chart, width=5.0*inch, height=3.0*inch))
            elements.append(Spacer(1, 10))
            
            # Add page break every 2 charts to avoid bunching
            if (i + 1) % 2 == 0 and i < len(chart_paths) - 1:
                elements.append(PageBreak())
    
    elements.append(Spacer(1, 8))
    elements.append(PageBreak())
    
    # ====== STATISTICAL DETAILS (for reference) ======
    if statistical_summary:
        elements.append(Paragraph("<b>📊 Statistical Summary</b>", section_style))
        elements.append(Spacer(1, 8))
        
        for col_name, stats in list(statistical_summary.items())[:6]:
            elements.append(Paragraph(f"<b>{col_name}</b>", styles["Heading3"]))
            
            stat_text = (f"Mean: {stats.get('mean', 'N/A'):.2f} | "
                        f"Median: {stats.get('median', 'N/A'):.2f} | "
                        f"Std: {stats.get('std', 'N/A'):.2f} | "
                        f"Range: {stats.get('min', 'N/A'):.2f}–{stats.get('max', 'N/A'):.2f}")
            
            elements.append(Paragraph(stat_text, styles["Normal"]))
            elements.append(Spacer(1, 6))
    
    elements.append(Spacer(1, 6))
    elements.append(PageBreak())    
    # ====== RECOMMENDATIONS & NEXT STEPS ======
    elements.append(Paragraph("<b>💡 Recommendations & Next Steps</b>", section_style))
    elements.append(Spacer(1, 8))
    
    recommendations = [
        "Review detected outliers before final analysis",
        "Monitor high-variance features for stability",
        "Validate strong correlations for causality",
        "Check domain assumptions with experts",
        "Schedule periodic data quality reviews"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        elements.append(Paragraph(f"<b>{i}.</b> {rec}", styles["Normal"]))
    
    elements.append(Spacer(1, 20))
    
    # ====== FOOTER ======
    footer_text = f"<i>Report generated {timestamp} | Confidential</i>"
    elements.append(Paragraph(footer_text, styles["Normal"]))
    
    doc.build(elements)
    return report_path