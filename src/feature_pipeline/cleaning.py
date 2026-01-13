"""Transcript cleaning utilities."""
import re
import pandas as pd
from typing import Optional


class TranscriptCleaner:
    """
    Cleans transcript data by removing:
    - Short text (<min_length chars)
    - Non-English text (non-ASCII)
    - Repetitive content (<unique_ratio unique words)
    """

    _NON_ASCII = re.compile(r'[^\x00-\x7F]')

    def __init__(self, text_col: str = "transcript", min_length: int = 80, unique_ratio: float = 0.3):
        self.text_col = text_col
        self.min_length = min_length
        self.unique_ratio = unique_ratio
        self._dropped: dict[str, pd.DataFrame] = {}

    def clean(self, df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
        """Apply all cleaning rules and return cleaned DataFrame."""
        df = df.copy().reset_index(drop=True)

        if self.text_col not in df.columns:
            print(f"⚠️ Column '{self.text_col}' not found. Skipping text cleaning.")
            return df

        initial_count = len(df)
        self._dropped = {}

        # Apply rules sequentially, recomputing text series after each filter
        for name, mask_fn in [
            ("short", lambda t: t.str.len() < self.min_length),
            ("non_english", lambda t: t.str.contains(self._NON_ASCII, na=False)),
            ("repetitive", lambda t: t.apply(self._is_repetitive)),
        ]:
            text = df[self.text_col].astype(str).str.strip()
            mask = mask_fn(text)
            self._dropped[name] = df[mask]
            df = df[~mask].reset_index(drop=True)

        if verbose:
            self._print_report(initial_count, len(df))

        return df

    def _is_repetitive(self, text: str) -> bool:
        words = text.lower().split()
        return bool(words) and len(set(words)) < self.unique_ratio * len(words)

    def _print_report(self, initial: int, final: int) -> None:
        print("🧹 Cleaning Report:")
        print(f"   - Short (<{self.min_length} chars): {len(self._dropped.get('short', []))}")
        print(f"   - Non-English: {len(self._dropped.get('non_english', []))}")
        print(f"   - Repetitive: {len(self._dropped.get('repetitive', []))}")
        print(f"   ✅ Kept {final}/{initial} rows")

    def get_dropped(self, rule: Optional[str] = None) -> pd.DataFrame:
        """Get dropped rows by rule name or all combined."""
        if rule:
            return self._dropped.get(rule, pd.DataFrame()).copy()
        return pd.concat(self._dropped.values(), ignore_index=True).drop_duplicates()
