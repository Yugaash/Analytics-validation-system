def compute_health_score(profile, quality):
    score = 100
    reasons = []

    # ---- Date issues ----
    score -= 5 * len(quality.get("date_like_columns", []))
    if quality.get("date_like_columns"):
        reasons.append("Date columns detected but not converted")

    score -= 3 * len(quality.get("ambiguous_date_columns", []))
    if quality.get("ambiguous_date_columns"):
        reasons.append("Ambiguous date columns detected")

    # ---- Identifier issues ----
    score -= 5 * len(quality.get("identifier_columns", []))
    if quality.get("identifier_columns"):
        reasons.append("Identifier columns present")

    score -= 3 * len(quality.get("ambiguous_identifier_columns", []))
    if quality.get("ambiguous_identifier_columns"):
        reasons.append("Ambiguous identifier columns present")

    # ---- Constant columns ----
    score -= 5 * len(quality.get("constant_columns", []))
    if quality.get("constant_columns"):
        reasons.append("Constant columns detected")

    # ---- Missing values ----
    missing = profile.get("missing_values", {})
    high_missing = [k for k, v in missing.items() if v > 0.05]

    if high_missing:
        score -= 10
        reasons.append("High missing values in some columns")

    # ---- Numeric usability ----
    if not quality.get("usable_numeric_columns"):
        score -= 30
        reasons.append("No usable numeric columns")

    # Clamp score
    score = max(score, 0)

    # Risk label
    if score >= 85:
        risk = "LOW"
    elif score >= 60:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    return {
        "health_score": score,
        "risk_level": risk,
        "reasons": reasons
    }
