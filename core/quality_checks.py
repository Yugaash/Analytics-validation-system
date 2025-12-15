import pandas as pd
import re

# -------- Patterns --------
DATE_NAME_PATTERN = re.compile(r"(date|time|dt)", re.IGNORECASE)
ID_NAME_PATTERN = re.compile(r"(id|code|zip|postal)", re.IGNORECASE)

DATE_VALUE_PATTERN = re.compile(
    r"""^(
        \d{4}[/-]\d{1,2}[/-]\d{1,2} |     # YYYY-MM-DD
        \d{1,2}[/-]\d{1,2}[/-]\d{2,4}     # DD-MM-YYYY or MM-DD-YYYY
    )$""",
    re.VERBOSE
)

def date_confidence(series, col_name):
    score = 0.0
    sample = series.dropna().astype(str).head(50)

    if sample.empty:
        return 0.0

    # Signal 1: column name
    if DATE_NAME_PATTERN.search(col_name):
        score += 0.4

    # Signal 2: value pattern consistency
    matches = sample.apply(lambda x: bool(DATE_VALUE_PATTERN.match(x)))
    score += 0.6 * matches.mean()

    return min(score, 1.0)


def id_confidence(series, col_name):
    score = 0.0
    nunique = series.nunique(dropna=True)
    ratio = nunique / len(series)

    # Signal 1: column name
    if ID_NAME_PATTERN.search(col_name):
        score += 0.4

    # Signal 2: high cardinality
    if ratio > 0.85:
        score += 0.4

    # Signal 3: numeric identifier tendency
    if pd.api.types.is_numeric_dtype(series):
        score += 0.2

    return min(score, 1.0)


def run_quality_checks(df):
    results = {
        "date_like_columns": [],
        "ambiguous_date_columns": [],
        "identifier_columns": [],
        "ambiguous_identifier_columns": [],
        "constant_columns": [],
        "usable_numeric_columns": [],
        "usable_categorical_columns": []
    }

    for col in df.columns:
        series = df[col]
        col_lower = col.lower()
        nunique = series.nunique(dropna=True)

        # -------- Constant column --------
        if nunique <= 1:
            results["constant_columns"].append(col)
            continue

        # -------- Object columns --------
        if series.dtype == "object":
            d_score = date_confidence(series, col_lower)

            if d_score >= 0.7:
                results["date_like_columns"].append(col)
            elif d_score >= 0.4:
                results["ambiguous_date_columns"].append(col)
            else:
                results["usable_categorical_columns"].append(col)
            continue

        # -------- Numeric columns --------
        if pd.api.types.is_numeric_dtype(series):
            i_score = id_confidence(series, col_lower)

            if i_score >= 0.7:
                results["identifier_columns"].append(col)
            elif i_score >= 0.4:
                results["ambiguous_identifier_columns"].append(col)
            else:
                results["usable_numeric_columns"].append(col)

    return results
