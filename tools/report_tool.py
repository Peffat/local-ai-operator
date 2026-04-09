from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os

REPORT_DIR = "outputs/reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def generate_pdf_report(insights, cleaning_steps, chart_paths, chart_insights, data_summary=None, 
                        data_quality_metrics=None, statistical_summary=None, skipped_columns=None, 
                        story_charts=None, data_understanding=None, initial_insights=None, 
                        analysis_suggestions=None, premium_story=None):
    """Generate a clean, professional PDF report with insights and charts."""
    
    report_path = os.path.join(REPORT_DIR, f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    doc = SimpleDocTemplate(report_path, topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.7*inch, rightMargin=0.7*inch)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6,
        alignment=1
    )
    
    section_style = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2e5c8a'),
        spaceAfter=8,
        spaceBefore=4,
        borderPadding=2
    )
    
    elements = []
    
    # ═══ TITLE PAGE ═══
    elements.append(Spacer(1, 0.12*inch))
    elements.append(Paragraph("<b>📊 Data Analysis Report</b>", title_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<i>AI-Powered Insights</i>", styles["Normal"]))
    elements.append(Spacer(1, 0.08*inch))
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"<b>Generated:</b> {timestamp}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Engine:</b> Ollama with Gemma4", styles["Normal"]))
    
    elements.append(Spacer(1, 0.12*inch))
    if data_quality_metrics:
        elements.append(Paragraph(
            f"<b>Records:</b> {data_quality_metrics.get('total_records', 0):,} | "
            f"<b>Columns:</b> {data_quality_metrics.get('total_columns', 0)}", 
            styles["Normal"]
        ))
        elements.append(Paragraph(
            f"<b>Quality Score:</b> {data_quality_metrics.get('quality_score', 0):.0f}% | "
            f"<b>Completeness:</b> {data_quality_metrics.get('completeness_pct', 0):.0f}%", 
            styles["Normal"]
        ))
        elements.append(Spacer(1, 0.2*inch))
    
    # ═══ EXECUTIVE SUMMARY ═══
    elements.append(Paragraph("<b>📈 Executive Summary</b>", section_style))
    elements.append(Spacer(1, 4))
    
    if data_quality_metrics:
        summary_text = f"""
        <b>Dataset:</b> {data_quality_metrics.get('total_records', 0):,} records analyzed<br/>
        <b>Data Quality:</b> {data_quality_metrics.get('quality_score', 0):.0f}% clean<br/>
        <b>Status:</b> Ready for insights
        """
        elements.append(Paragraph(summary_text, styles["Normal"]))

    if data_understanding:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("<b>🔍 Data Understanding</b>", section_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(data_understanding.replace("\n", "<br/>"), styles["Normal"]))
        elements.append(Spacer(1, 6))
    
    # ═══ KEY INSIGHTS ═══
    elements.append(Paragraph("<b>💡 Key Insights</b>", section_style))
    elements.append(Spacer(1, 4))
    if premium_story:
        elements.append(Paragraph("<b>📌 Premium Story</b>", styles["Heading3"]))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(premium_story, styles["Normal"]))
        elements.append(Spacer(1, 6))
    
    if isinstance(insights, str):
        insight_lines = insights.split("\n")
    else:
        insight_lines = insights
    
    # Map charts to insights
    chart_map = {}
    if story_charts:
        for j, chart_info in enumerate(story_charts):
            if 'story_index' in chart_info:
                chart_map[chart_info['story_index']] = chart_info
    
    # Display insights with their charts
    for idx, line in enumerate([l for l in insight_lines if l.strip()][:6]):
        line = line.strip().lstrip('•').strip()
        
        if line:
            # Parse insight
            if '|' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                title = parts[0]
                content = ' '.join(parts[1:]) if len(parts) > 1 else ""
            else:
                title = f"Finding {idx + 1}"
                content = line
            
            elements.append(Paragraph(f"<b>{title}</b>", styles["Heading3"]))
            elements.append(Spacer(1, 3))
            if content:
                elements.append(Paragraph(content, styles["Normal"]))
            
            if idx in chart_map and os.path.exists(chart_map[idx]['path']):
                elements.append(Spacer(1, 5))
                try:
                    elements.append(Image(chart_map[idx]['path'], width=5.5*inch, height=3.2*inch))
                except Exception as e:
                    elements.append(Paragraph(f"<i>[Chart unavailable: {str(e)}]</i>", styles["Normal"]))
                if chart_map[idx].get('caption'):
                    elements.append(Spacer(1, 3))
                    elements.append(Paragraph(f"<i>{chart_map[idx]['caption']}</i>", styles["Normal"]))

            elements.append(Spacer(1, 5))
    
    elements.append(Spacer(1, 6))
    
    # ═══ DATA QUALITY ═══
    if data_quality_metrics:
        elements.append(Paragraph("<b>🧹 Data Quality</b>", section_style))
        elements.append(Spacer(1, 4))
        
        metrics_data = [
            ["Metric", "Value"],
            ["Total Records", str(data_quality_metrics.get('total_records', 'N/A'))],
            ["Completeness", f"{data_quality_metrics.get('completeness_pct', 0):.0f}%"],
            ["Quality Score", f"{data_quality_metrics.get('quality_score', 0):.0f}%"],
        ]
        
        table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))

    if statistical_summary is not None:
        try:
            top_columns = list(statistical_summary.columns[:4])
            stat_rows = [
                ["Statistic"] + [col.title() for col in top_columns],
            ]
            for metric in ["mean", "std", "min", "max"]:
                if metric in statistical_summary.index:
                    stat_rows.append([
                        metric.title(),
                        *[f"{statistical_summary.loc[metric, col]:.1f}" for col in top_columns]
                    ])
            stat_table = Table(stat_rows, colWidths=[2*inch] + [1.5*inch]*len(top_columns))
            stat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
            ]))
            elements.append(Paragraph("<b>📊 Statistical Highlights</b>", section_style))
            elements.append(Spacer(1, 6))
            elements.append(stat_table)
            elements.append(Spacer(1, 12))
        except Exception:
            pass
    
    # ═══ DATA PREPARATION ═══
    if cleaning_steps:
        elements.append(Paragraph("<b>✓ Data Preparation</b>", section_style))
        elements.append(Spacer(1, 4))
        for step in cleaning_steps:
            elements.append(Paragraph(f"• {step}", styles["Normal"]))
        elements.append(Spacer(1, 10))

    if analysis_suggestions:
        elements.append(Paragraph("<b>🧠 Analyst Recommendations</b>", section_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(analysis_suggestions.replace("\n", "<br/>"), styles["Normal"]))
        elements.append(Spacer(1, 10))

    # ═══ RECOMMENDATIONS ═══
    elements.append(Paragraph("<b>→ Recommendations</b>", section_style))
    elements.append(Spacer(1, 4))
    
    recommendations = [
        "Review the key insights and charts above",
        "Use the cleaned dataset for further analysis",
        "Validate recommendations with domain experts",
        "Monitor data quality for future uploads"
    ]
    
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", styles["Normal"]))
    
    elements.append(Spacer(1, 12))
    
    # ═══ FOOTER ═══
    footer = f"<i>Report generated {timestamp} | Confidential</i>"
    elements.append(Paragraph(footer, styles["Normal"]))
    
    doc.build(elements)
    return report_path