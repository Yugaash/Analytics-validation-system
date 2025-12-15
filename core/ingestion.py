import pandas as pd

def load_dataset(file):
    
    df = pd.read_csv(file)

    if df.empty:
        raise ValueError("Dataset is empty or invalid")

    return df
