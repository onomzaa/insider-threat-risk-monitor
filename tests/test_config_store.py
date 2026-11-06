import tempfile
import unittest
from pathlib import Path
from modules.config_store import DEFAULTS, load_config, save_config, validate_config


class ConfigStoreTests(unittest.TestCase):
    def test_defaults_when_file_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_config(Path(directory) / "missing.json"), DEFAULTS)

    def test_save_and_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            custom = {"correlation_window_minutes": 45, "medium_risk_threshold": 35, "high_risk_threshold": 75}
            save_config(custom, path)
            self.assertEqual(load_config(path), custom)

    def test_invalid_threshold_order_rejected(self):
        with self.assertRaises(ValueError):
            validate_config({"correlation_window_minutes": 60, "medium_risk_threshold": 80, "high_risk_threshold": 70})

    def test_invalid_window_rejected(self):
        with self.assertRaises(ValueError):
            validate_config({"correlation_window_minutes": 2, "medium_risk_threshold": 40, "high_risk_threshold": 70})


if __name__ == "__main__":
    unittest.main()
