import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_file(filepath: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(filepath)
        logging.info("Loaded as CSV.")
        return df
    except pd.errors.ParserError:
        try:
            df = pd.read_csv(filepath, sep='\t')
            logging.info("Loaded as TSV.")
            return df
        except pd.errors.ParserError:
            try:
                df = pd.read_csv(filepath, delim_whitespace=True)
                logging.info("Loaded as space-delimited.")
                return df
            except pd.errors.ParserError:
                try:
                    df = pd.read_csv(filepath, header=None)
                    logging.info("Loaded with no headers.")
                    return df
                except Exception as e:
                    logging.error("File loading failed: %s", e)
                    return None

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    # Columns to clean and fill
    fill_cols = [
        "QTY_ON_HND", "MTD", "YTD", "FIRST", "SECON", "THIRD", "FOURT",
        "FIFTH", "SIXTH", "SEVEN", "EIGHT", "NINTH", "TENTH", "ELEVE",
        "TWELV", "PRIORY", "SALES"
    ]
    df[fill_cols] = df[fill_cols].fillna(0).astype(int)

    # Weekly average column
    week_cols = fill_cols[3:15]  # FIRST to TWELV
    df["AVG_WEEK"] = np.ceil(df[week_cols].sum(axis=1) / 48).astype(int)

    # # Unstock items flag
    # df["UNSTOCK_ITEMS"] = df[fill_cols].isnull().all(axis=1).astype(int)

    columns_to_check = [
    "QTY_ON_HND", "FIRST", "SECON", "THIRD", "FOURT", "FIFTH", "SIXTH",
    "SEVEN", "EIGHT", "NINTH", "TENTH", "ELEVE", "TWELV"
]

    # Mark UNSTOCK_ITEMS = 1 if all values in these columns are zero
    df["UNSTOCK_ITEMS"] = (df[columns_to_check].sum(axis=1) == 0).astype(int)


    # SLOW_ITEMS condition: Qty available, slow sales, and price under 50
    df["WEEK_SUM"] = df[week_cols].sum(axis=1)
    df["SLOW_ITEMS"] = (
        (df["QTY_ON_HND"].notnull()) &
        (df["WEEK_SUM"].between(0, 10)) &
        (df["PRICE"] < 50)
    ).astype(int)

    # NXT_ORDER flag based on projected weeks
    df["NXT_ORDER"] = (
        (df["AVG_WEEK"] > df["QTY_ON_HND"]) |
        (df["AVG_WEEK"] + 1 > df["QTY_ON_HND"]) |
        (df["AVG_WEEK"] + 2 > df["QTY_ON_HND"])
    ).astype(int)

    return df

def main():
    filepath = 'Fi.txt'
    df = load_file(filepath)
    if df is not None:
        df = preprocess_data(df)
        return df
    else:
        logging.error("Failed to load and process the file.")
        return pd.DataFrame()

# If you want to run this standalone
if __name__ == "__main__":
    df = main()
    print(df.head(100))
