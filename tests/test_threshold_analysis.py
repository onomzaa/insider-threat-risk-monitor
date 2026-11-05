import pandas as pd
import pytest
from evaluation.threshold_analysis import analyze_thresholds


def test_threshold_analysis_reports_tradeoff():
    sample = pd.DataFrame({
        "ground_truth": [1, 1, 0, 0],
        "improved_risk_score": [85, 55, 65, 20],
    })
    result = analyze_thresholds(sample, thresholds=[50, 70])
    at_50 = result[result["threshold"] == 50].iloc[0]
    at_70 = result[result["threshold"] == 70].iloc[0]
    assert at_50["TP"] == 2
    assert at_50["FP"] == 1
    assert at_70["TP"] == 1
    assert at_70["FP"] == 0
    assert at_70["FN"] == 1


def test_threshold_out_of_range_rejected():
    sample = pd.DataFrame({"ground_truth": [1], "improved_risk_score": [80]})
    with pytest.raises(ValueError):
        analyze_thresholds(sample, thresholds=[101])
