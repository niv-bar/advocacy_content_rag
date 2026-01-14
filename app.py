"""
Jewish Advocacy Response Viewer
Streamlit app to browse generated responses by query and method.
"""
import json
import streamlit as st
import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================
DATA_PATH = Path(__file__).parent / "data" / "inference_results.csv"

METHOD_DISPLAY_NAMES = {
    "control": "Control",
    "strategic_empathy": "Strategic Empathy",
    "reactance_avoidance": "Reactance Avoidance",
    "authenticity_narrative": "Authenticity & Narrative",
    "style_transfer": "Style Transfer"
}


# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_data():
    """Load and parse the inference results CSV."""
    df = pd.read_csv(DATA_PATH)
    return df


def parse_json_column(json_str: str) -> dict:
    """Safely parse JSON string to dict."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return {}


# ============================================================
# STREAMLIT APP
# ============================================================
def main():
    # Page config
    st.set_page_config(
        page_title="Jewish Advocacy Response Viewer",
        page_icon="✡️",
        layout="wide"
    )

    # Title
    st.title("✡️ Jewish Advocacy Response Viewer")
    st.markdown("Browse generated responses using different affective messaging methods.")
    st.markdown("---")

    # Load data
    try:
        df = load_data()
    except FileNotFoundError:
        st.error(f"❌ CSV file not found at: {DATA_PATH}")
        st.info("Please place 'inference_results.csv' in the 'data' folder.")
        return

    # --------------------------------------------------------
    # STEP 1: Select Query
    # --------------------------------------------------------
    st.subheader("1️⃣ Select a Query")

    queries = df["query"].tolist()
    selected_query = st.selectbox(
        "Choose a question:",
        options=queries,
        index=0,
        label_visibility="collapsed"
    )

    # Get selected row
    row = df[df["query"] == selected_query].iloc[0]

    # Parse JSON columns
    transcripts = parse_json_column(row["top3_transcripts"])
    responses = parse_json_column(row["llm_response"])

    st.markdown("---")

    # --------------------------------------------------------
    # STEP 2: Display Sources
    # --------------------------------------------------------
    st.subheader("2️⃣ Related Sources")

    # Create 3 columns for sources
    cols = st.columns(3)

    for i, (rank, source) in enumerate(transcripts.items()):
        with cols[i]:
            st.markdown(f"### 📎 Source {rank}")
            st.metric("Score", f"{source.get('score', 'N/A')}")

            st.markdown(f"**Main Topic:** {source.get('main_subject', 'N/A')}")
            st.markdown(f"**Sub Topic:** {source.get('sub_topic', 'N/A')}")
            st.markdown(f"**Question:** {source.get('question', 'N/A')}")

            with st.expander("📜 View Transcript"):
                st.write(source.get('transcript', 'No transcript available'))

            link = source.get('link', '')
            if link:
                st.markdown(f"[🔗 Open Instagram Link]({link})")

    st.markdown("---")

    # --------------------------------------------------------
    # STEP 3: Select Method
    # --------------------------------------------------------
    st.subheader("3️⃣ Select Messaging Method")

    method_options = list(METHOD_DISPLAY_NAMES.keys())
    method_labels = list(METHOD_DISPLAY_NAMES.values())

    selected_method = st.radio(
        "Choose a method:",
        options=method_options,
        format_func=lambda x: METHOD_DISPLAY_NAMES[x],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # --------------------------------------------------------
    # STEP 4: Display Response
    # --------------------------------------------------------
    st.subheader(f"4️⃣ Generated Response ({METHOD_DISPLAY_NAMES[selected_method]})")

    response_text = responses.get(selected_method, "No response available for this method.")

    # Display response in a nice box
    st.info(response_text)

# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    main()