"""Feature Pipeline: Merge -> Clean -> Save"""
import os
import pandas as pd
import hashlib

from src.feature_pipeline.data_normalization import ExcelLoader
from src.feature_pipeline.cleaning import TranscriptCleaner
from src.core.config import settings


class FeaturePipeline:
    """Orchestrates the data cleaning and preparation pipeline."""

    URL_PATTERN = r'(https?://\S+)'

    def __init__(
            self,
            excel_filename: str = "riseapp_hot_topics.xlsx",
            transcripts_filename: str = "rise_app_data_with_transcripts.csv",
            output_filename: str = "rise_app_clean.csv",
            dropped_filename: str = "dropped_rows.csv",
    ):
        self.excel_path = os.path.join(settings.DATA_DIR, excel_filename)
        self.transcripts_path = os.path.join(settings.DATA_DIR, transcripts_filename)
        self.output_path = os.path.join(settings.DATA_DIR, output_filename)
        self.dropped_path = os.path.join(settings.DATA_DIR, dropped_filename)

        self.cleaner = TranscriptCleaner(text_col="transcript")
        self._final_cols = ['id', 'link_id', 'main_subject', 'sub_topic', 'question', 'link_cleaned', 'transcript']

    def run(self) -> pd.DataFrame:
        """Execute the full pipeline."""
        print("🚀 Starting Feature Pipeline...")

        self._validate_inputs()

        df = self._load_and_merge()
        df = self._clean(df)
        df = self._postprocess(df)
        self._save(df)

        return df

    def _validate_inputs(self) -> None:
        missing = [p for p in [self.excel_path, self.transcripts_path] if not os.path.exists(p)]
        if missing:
            raise FileNotFoundError(f"Missing input files: {missing}")

    def _load_and_merge(self) -> pd.DataFrame:
        """Load Excel + CSV and merge on normalized link."""
        # Load Excel metadata
        loader = ExcelLoader(self.excel_path)
        df_meta = pd.DataFrame([row.model_dump() for row in loader.load()])

        # Filter Instagram only
        df_meta = df_meta[df_meta['social_network'] == 'Instagram'].copy()
        print(f"📊 Instagram rows: {len(df_meta)}")

        # Load transcripts
        df_transcripts = pd.read_csv(self.transcripts_path)

        # Normalize join keys
        df_meta['join_key'] = df_meta['link'].astype(str).str.strip().str.lower()

        link_col = 'Link' if 'Link' in df_transcripts.columns else 'link'
        df_transcripts['join_key'] = df_transcripts[link_col].astype(str).str.strip().str.lower()
        df_transcripts = df_transcripts.drop_duplicates(subset=['join_key'])

        # Merge
        df = pd.merge(df_meta, df_transcripts[['join_key', 'Transcript']], on='join_key', how='left')
        df.rename(columns={'Transcript': 'transcript'}, inplace=True)

        return df

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply cleaning rules."""
        print("\n🧼 Running Data Cleaning...")

        # Treat 'nan' string as null
        df['transcript'] = df['transcript'].replace('nan', pd.NA)

        # Drop missing required fields
        before = len(df)
        df = df.dropna(subset=['transcript'])
        print(f"   - Dropped {before - len(df)} rows missing transcript")

        # Apply text-based cleaning
        df = self.cleaner.clean(df)

        return df

    def _postprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """URL extraction, dedup checks, and final cleanup."""
        # Extract clean URLs
        df['link_cleaned'] = df['link'].str.extract(self.URL_PATTERN, expand=False)

        # Flag duplicate IDs (warning only)
        df['is_duplicate_id'] = df.duplicated(subset=['id'], keep=False)
        dup_count = df['is_duplicate_id'].sum()
        if dup_count > 0:
            print(f"⚠️ Warning: {dup_count} rows with duplicate IDs")

        # Normalize missing question values
        df['question'] = df['question'].replace(['missing question', 'Unknown Question'], pd.NA)

        df["link_id"] = df["link_cleaned"].apply(
            lambda x: int(hashlib.sha256(x.encode()).hexdigest()[:16], 16)
        )

        return df

    def _save(self, df: pd.DataFrame) -> None:
        """Save clean data and dropped rows."""
        df[self._final_cols].to_csv(self.output_path, index=False, encoding='utf-8-sig')

        df_dropped = self.cleaner.get_dropped()
        if not df_dropped.empty:
            df_dropped.to_csv(self.dropped_path, index=False, encoding='utf-8-sig')

        print(f"\n✅ Pipeline Complete!")
        print(f"   💾 Clean: {self.output_path} ({len(df)} rows)")
        print(f"   🗑️ Dropped: {self.dropped_path} ({len(df_dropped)} rows)")