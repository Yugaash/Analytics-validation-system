def profile_data(df):
    summary = {}

    summary["rows"] = df.shape[0]
    summary["columns"] = df.shape[1]

    summary["missing_values"] = (
        df.isnull().mean().round(3).to_dict()
    )

    summary["numeric_columns"] = (
        df.select_dtypes(include="number")
        .columns.tolist()
    )

    summary["categorical_columns"] = (
        df.select_dtypes(exclude="number")
        .columns.tolist()
    )

    return summary
