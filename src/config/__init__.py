"""Configuration loader for feature pipeline."""
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "feature_pipeline_config.json"


def load_config() -> dict:
    """Load and return the feature pipeline configuration."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


config = load_config()