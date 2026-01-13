"""ETL utilities for loading and normalizing Excel data."""
import hashlib
import pandas as pd
from typing import Optional

from src.core.models import RawDataRow
from src.config import config


class ExcelLoader:
    """Loads and normalizes multi-sheet Excel files into structured data."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._social_networks = config["social_networks"]
        self._defaults = config["defaults"]

    def load(self) -> list[RawDataRow]:
        """Load all sheets and return list of validated RawDataRow objects."""
        print(f"📂 Loading: {self.file_path}...")

        sheets = pd.read_excel(self.file_path, sheet_name=None, header=None)
        rows = []

        for sheet_name, df in sheets.items():
            if not df.empty:
                rows.extend(self._process_sheet(str(sheet_name), df))

        print(f"✅ Extracted {len(rows)} valid rows")
        return rows

    def _process_sheet(self, sheet_name: str, df: pd.DataFrame) -> list[RawDataRow]:
        """Process a single sheet, tracking sub-topic state."""
        rows = []
        current_sub_topic = self._defaults["sub_topic"]

        for row in df.itertuples(index=False, name=None):
            col_a = self._safe_str(row, 0)
            col_b = self._safe_str(row, 1)
            col_c = self._safe_str(row, 2)

            if not col_a and not col_b:
                continue

            # Data row: has link or status
            if col_b or col_c:
                question = col_a or self._defaults["unknown_question"]
                try:
                    rows.append(RawDataRow(
                        id=self._hash(question, col_b),
                        main_subject=sheet_name,
                        sub_topic=current_sub_topic,
                        question=question,
                        link=col_b,
                        social_network=self._detect_network(col_b),
                    ))
                except Exception as e:
                    print(f"⚠️ Skipping invalid row in {sheet_name}: {e}")
            # Header row: update sub-topic
            elif col_a:
                current_sub_topic = col_a

        return rows

    @staticmethod
    def _safe_str(row: tuple, idx: int) -> Optional[str]:
        """Safely extract and strip string from tuple index."""
        if idx < len(row) and pd.notna(row[idx]):
            val = str(row[idx]).strip()
            return val if val else None
        return None

    def _detect_network(self, link: Optional[str]) -> str:
        """Identify social network from URL."""
        if not link:
            return self._defaults["no_link_network"]
        link_lower = link.lower()
        for keyword, network in self._social_networks.items():
            if keyword in link_lower:
                return network
        return self._defaults["other_network"]

    @staticmethod
    def _hash(content: str, link: Optional[str]) -> str:
        """Generate deterministic MD5 hash ID."""
        return hashlib.md5(f"{content}{link or ''}".encode()).hexdigest()