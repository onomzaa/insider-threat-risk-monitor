"""Safe loader for synthetic detection-evaluation metrics."""
from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {
    "method", "precision", "recall", "F1", "false_positive_rate",
    "TP", "FP", "TN", "FN",
}


def load_evaluation_metrics(path):
    """Load and validate the metrics CSV; return an empty frame if absent."""
    source = Path(path)
    if not source.exists():
        return pd.DataFrame()
    frame = pd.read_csv(source)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError("Evaluation metrics file is missing columns: " + ", ".join(sorted(missing)))
    return frame
