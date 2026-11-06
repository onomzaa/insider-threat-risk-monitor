"""Local configuration for the research dashboard; stores only numeric settings."""
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "data" / "system_config.json"
DEFAULTS = {"correlation_window_minutes": 60, "high_risk_threshold": 70, "medium_risk_threshold": 40}


def load_config(path=CONFIG_PATH):
    config = dict(DEFAULTS)
    source = Path(path)
    if source.exists():
        try:
            saved = json.loads(source.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                config.update({key: saved[key] for key in DEFAULTS if key in saved})
        except (json.JSONDecodeError, OSError):
            raise ValueError("Configuration file is unreadable; inspect system_config.json")
    validate_config(config)
    return config


def validate_config(config):
    window = config.get("correlation_window_minutes")
    high = config.get("high_risk_threshold")
    medium = config.get("medium_risk_threshold")
    if not isinstance(window, int) or not 5 <= window <= 240:
        raise ValueError("Correlation window must be 5–240 minutes")
    if not isinstance(high, int) or not 50 <= high <= 100:
        raise ValueError("High-risk threshold must be 50–100")
    if not isinstance(medium, int) or not 10 <= medium < high:
        raise ValueError("Medium threshold must be 10 and lower than high threshold")
    return True


def save_config(config, path=CONFIG_PATH):
    validate_config(config)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return dict(config)
