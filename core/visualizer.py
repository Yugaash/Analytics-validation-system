import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def render_visual(insight, df):
    itype = insight["type"]

    # -------------------------------
    # 1. NUMERIC SUMMARY
    # Line / Area chart
    # -------------------------------
    if itype == "numeric_summary":
        col = insight["column"]

        st.line_chart(df[col])

        with st.expander("📈 Alternative View (Area Chart)"):
            st.area_chart(df[col])

    # -------------------------------
    # 2. CATEGORICAL DISTRIBUTION
    # Bar chart
    # -------------------------------
    elif itype == "categorical_distribution":
        col = insight["column"]
        data = df[col].value_counts().head(10)

        st.bar_chart(data)

    # -------------------------------
    # 3. GROUP COMPARISON
    # Bar + Radar-like chart
    # -------------------------------
    elif itype == "group_comparison":
        num = insight["metric"]
        cat = insight["group_by"]

        data = (
            df.groupby(cat)[num]
            .mean()
            .sort_values(ascending=False)
            .head(6)
        )

        # ---- Bar Chart ----
        st.bar_chart(data)

        # ---- Radar Chart ----
        with st.expander("🕸️ Radar Comparison"):
            labels = data.index.tolist()
            values = data.values.tolist()

            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
            values += values[:1]
            angles = np.concatenate([angles, [angles[0]]])

            fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
            ax.plot(angles, values, linewidth=2)
            ax.fill(angles, values, alpha=0.25)

            ax.set_thetagrids(np.degrees(angles[:-1]), labels)
            ax.set_title(f"{num} by {cat}", pad=20)

            st.pyplot(fig)
