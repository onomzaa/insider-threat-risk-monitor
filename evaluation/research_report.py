"""Create a cautious research evaluation report from local synthetic evaluation outputs."""
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

def _read_csv(path):
    return pd.read_csv(path) if path.exists() else None

def build_report(results_dir=RESULTS):
    results_dir = Path(results_dir)
    metrics = _read_csv(results_dir / "evaluation_metrics.csv")
    predictions = _read_csv(results_dir / "scenario_predictions.csv")
    thresholds = _read_csv(results_dir / "threshold_analysis.csv")
    if metrics is None or predictions is None:
        raise FileNotFoundError("Run python -m evaluation.evaluate first to create evaluation_metrics.csv and scenario_predictions.csv.")
    required_metrics = {"method", "TP", "FP", "TN", "FN", "precision", "recall", "F1", "false_positive_rate"}
    if not required_metrics.issubset(metrics.columns):
        raise ValueError(f"Metrics file missing columns: {sorted(required_metrics - set(metrics.columns))}")
    required_predictions = {"employee_id", "ground_truth", "baseline_detected", "improved_risk_score", "improved_detected"}
    if not required_predictions.issubset(predictions.columns):
        raise ValueError(f"Predictions file missing columns: {sorted(required_predictions - set(predictions.columns))}")
    lines = [
        "# Research Evaluation Report",
        "",
        "**Project:** Insider Threats in Organizations: Causes, Warning Signs, and Risk Management",
        "**System:** Insider Threat Risk Monitor (ITRM) — educational prototype",
        f"**Generated (UTC):** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Executive summary",
        "This report summarizes results from the project's labeled synthetic scenarios. These results describe only this constructed dataset and are not evidence of operational accuracy or effectiveness in a real organization.",
        "",
        "## Evaluation design",
        f"- Employee/account examples evaluated: **{predictions['employee_id'].nunique()}**",
        f"- Positive labels in the synthetic set: **{int(predictions['ground_truth'].sum())}**",
        f"- Baseline detections: **{int(predictions['baseline_detected'].sum())}**",
        f"- Improved-method detections: **{int(predictions['improved_detected'].sum())}**",
        "- Improved score threshold: **70** (prototype setting, not validated)",
        "",
        "## Detection metrics",
        "| Method | TP | FP | TN | FN | Precision | Recall | F1 | FPR |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in metrics.iterrows():
        lines.append("| " + " | ".join([
            str(row["method"]), str(int(row["TP"])), str(int(row["FP"])),
            str(int(row["TN"])), str(int(row["FN"])),
            f"{float(row['precision']):.3f}", f"{float(row['recall']):.3f}",
            f"{float(row['F1']):.3f}", f"{float(row['false_positive_rate']):.3f}"
        ]) + " |")
    lines += ["", "Metric definitions: precision = TP/(TP+FP); recall = TP/(TP+FN); F1 is the harmonic mean of precision and recall; false-positive rate = FP/(FP+TN). A zero denominator is represented as zero by the evaluation code.", ""]
    if thresholds is not None:
        lines += ["## Threshold sensitivity", "", "The following table is exploratory and uses the same synthetic scenario set; it is not independent validation.", ""]
        lines.append("| " + " | ".join(map(str, thresholds.columns)) + " |")
        lines.append("|" + "|".join(["---"] * len(thresholds.columns)) + "|")
        for _, row in thresholds.iterrows():
            lines.append("| " + " | ".join(str(v) for v in row.tolist()) + " |")
        lines.append("")
    lines += [
        "## Interpretation",
        "- Compare the methods using the displayed confusion counts as well as summary metrics.",
        "- False positives represent synthetic benign examples flagged by the configured rules; false negatives represent labeled positive examples missed.",
        "- Small datasets can make metrics highly sensitive to individual examples and label choices.",
        "- Threshold selection is a trade-off and should not be treated as a universal operational setting.",
        "",
        "## Limitations",
        "- Labels and records are hand-authored synthetic scenarios.",
        "- Scenario coverage is limited and may not reflect actual organizational behavior.",
        "- The evaluation does not test deployment, analyst workload, adversarial adaptation, or production data quality.",
        "- No result establishes intent, culpability, or real-world detection performance.",
        "",
        "## Ethical and operational safeguards",
        "Use only synthetic or properly authorized data. Restrict access, minimize personal information, document reviews, and require a qualified human analyst to validate alerts before any consequential action.",
        "",
        "## Conclusion",
        "The experiment provides a reproducible classroom comparison of a baseline and a correlated/contextual prototype on a small synthetic dataset. Further independent, authorized, privacy-reviewed evaluation is required before any real-world claims or deployment.",
        "",
        "## Reproducibility",
        "```powershell",
        "python -m evaluation.evaluate",
        "python -m evaluation.threshold_analysis",
        "python -m evaluation.research_report",
        "```",
    ]
    return "\n".join(lines) + "\n"

def generate_report(results_dir=RESULTS):
    text = build_report(results_dir)
    path = Path(results_dir) / "research_evaluation_report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path

def generate_pdf(markdown_path=None, output_path=None):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError as exc:
        raise RuntimeError("PDF export requires ReportLab. Install with: python -m pip install reportlab") from exc
    markdown_path = Path(markdown_path or RESULTS / "research_evaluation_report.md")
    output_path = Path(output_path or RESULTS / "research_evaluation_report.pdf")
    if not markdown_path.exists():
        generate_report()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    for line in markdown_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("|"):
            continue
        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Heading2"]))
        elif line.strip():
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe, styles["BodyText"]))
            story.append(Spacer(1, 5))
        else:
            story.append(Spacer(1, 8))
    doc.build(story)
    return output_path

if __name__ == "__main__":
    path = generate_report()
    print(f"Markdown report saved: {path}")
    try:
        pdf = generate_pdf()
        print(f"PDF report saved: {pdf}")
    except RuntimeError as exc:
        print(exc)
