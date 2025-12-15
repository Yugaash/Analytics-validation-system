import sys
import os
import streamlit as st
import pandas as pd

# -------------------------------------------------
# Ensure project root is in path (Windows-safe)
# -------------------------------------------------
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ingestion import load_dataset
from core.profiling import profile_data
from core.quality_checks import run_quality_checks
from core.health_score import compute_health_score
from core.insight_engine import generate_insights
from core.visualizer import render_visual

# -------------------------------------------------
# Streamlit App Config
# -------------------------------------------------
st.set_page_config(
    page_title="Analytics Validation System",
    layout="wide"
)

st.title("📊 Analytics Validation System")
st.caption(
    "Upload any structured dataset to receive validated, safe analytics insights"
)

# -------------------------------------------------
# File Upload
# -------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        # -------------------------------------------------
        # Load Dataset
        # -------------------------------------------------
        df = load_dataset(uploaded_file)
        st.success("Dataset loaded successfully")

        # -------------------------------------------------
        # Dataset Preview
        # -------------------------------------------------
        st.subheader("🔎 Dataset Preview")
        st.dataframe(df.head())

        # -------------------------------------------------
        # Schema Detection
        # -------------------------------------------------
        st.subheader("🧬 Detected Schema")
        schema = df.dtypes.astype(str).to_dict()
        st.json(schema)

        # -------------------------------------------------
        # Data Profiling
        # -------------------------------------------------
        st.subheader("📈 Data Profiling Summary")
        profile = profile_data(df)
        st.json(profile)

        # -------------------------------------------------
        # Data Quality Checks
        # -------------------------------------------------
        st.subheader("🧪 Data Quality Checks")
        quality_report = run_quality_checks(df)
        st.json(quality_report)

        # -------------------------------------------------
        # Data Health Score
        # -------------------------------------------------
        st.subheader("🏥 Data Health Score")

        health = compute_health_score(profile, quality_report)

        st.metric(
            label="Overall Data Health Score",
            value=f"{health['health_score']} / 100",
            delta=health["risk_level"]
        )

        st.write("### ⚠️ Risk Factors")
        if health["reasons"]:
            for r in health["reasons"]:
                st.write(f"- {r}")
        else:
            st.write("No major risks detected")

        # -------------------------------------------------
        # Insight Generation
        # -------------------------------------------------
        st.subheader("💡 Generated Insights (Safe & Rule-Based)")

        insights = generate_insights(df, quality_report)

        if insights:
            for i, ins in enumerate(insights, 1):
                st.write(f"### Insight {i}")
                st.json(ins)

                # -------------------------------------------------
                # Visualization (ONLY for safe insight types)
                # -------------------------------------------------
                if ins["type"] in [
                    "numeric_summary",
                    "categorical_distribution",
                    "group_comparison"
                ]:
                    st.write("📊 Visualization")
                    render_visual(ins, df)

        else:
            st.write("No safe insights could be generated from this dataset.")

    except Exception as e:
        st.error(f"Error: {str(e)}")
