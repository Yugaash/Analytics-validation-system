import pandas as pd
import re

ID_NAME_PATTERN = re.compile(r"(^id$|_id$|id_|identifier)", re.IGNORECASE)

def generate_insights(df, quality):
    insights = []

    numeric_cols = quality.get("usable_numeric_columns", [])
    categorical_cols = quality.get("usable_categorical_columns", [])
    date_cols = quality.get("date_like_columns", [])

    # Explicitly blocked grouping columns
    blocked_group_cols = set(
        quality.get("identifier_columns", []) +
        quality.get("ambiguous_identifier_columns", [])
    )

    # -------------------------------------------------
    # 1. NUMERIC SUMMARY
    # -------------------------------------------------
    for col in numeric_cols:
        s = df[col]
        insights.append({
            "type": "numeric_summary",
            "column": col,
            "mean": round(s.mean(), 2),
            "median": round(s.median(), 2),
            "min": round(s.min(), 2),
            "max": round(s.max(), 2)
        })

    # -------------------------------------------------
    # 2. CATEGORICAL DISTRIBUTION
    # -------------------------------------------------
    for col in categorical_cols:
        vc = df[col].value_counts(normalize=True)
        if vc.empty:
            continue

        if vc.iloc[0] >= 0.4:
            insights.append({
                "type": "categorical_distribution",
                "column": col,
                "top_value": vc.index[0],
                "percentage": round(vc.iloc[0] * 100, 2)
            })

    # -------------------------------------------------
    # 3. GROUP COMPARISON (FINAL SAFE VERSION)
    # -------------------------------------------------
    for num_col in numeric_cols:
        for cat_col in categorical_cols:

            # ❌ Block known identifier columns
            if cat_col in blocked_group_cols:
                continue

            # ❌ Block semantic ID-like names (Order ID, Customer ID, etc.)
            if ID_NAME_PATTERN.search(cat_col.replace(" ", "_").lower()):
                continue

            grouped = df.groupby(cat_col)[num_col].mean()

            if grouped.nunique() <= 1:
                continue

            insights.append({
                "type": "group_comparison",
                "metric": num_col,
                "group_by": cat_col,
                "top_group": grouped.idxmax(),
                "value": round(grouped.max(), 2)
            })

            break  # prevent explosion

    # -------------------------------------------------
    # 4. TREND READINESS
    # -------------------------------------------------
    if date_cols and numeric_cols:
        insights.append({
            "type": "trend_readiness",
            "message": "Time-series trend analysis possible after date conversion",
            "date_columns": date_cols,
            "numeric_columns": numeric_cols
        })

    return insights
