import pandas as pd
import re
import logging
from sklearn.model_selection import train_test_split

# 🔹 Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_text_for_transformer(text):
    """Light cleaning for transformers"""
    if pd.isnull(text):
        return ""

    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s\-\'\.\,]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_text_for_baseline(text):
    """Aggressive cleaning for ML models"""
    if pd.isnull(text):
        return ""

    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def preprocess_dataset(input_path, text_column, label_column):
    df = pd.read_csv(input_path)
    df = df.dropna(subset=[text_column, label_column])

    df["clean_text"] = df[text_column].apply(clean_text_for_transformer)
    df["clean_text_baseline"] = df[text_column].apply(clean_text_for_baseline)

    # 🔥 Remove empty rows
    df = df[df["clean_text"].str.strip() != ""]

    df = df[["clean_text", "clean_text_baseline", label_column]]

    logger.info(f"Loaded {len(df)} samples")
    return df


def filter_invalid_samples(df):
    """
    ✅ Remove problematic samples that cause NaN gradients.
    - Too short text (< 10 chars)
    - Too long text (> 1000 chars)
    """
    initial_count = len(df)
    
    # Calculate text length
    df["text_len"] = df["clean_text"].str.len()
    
    # Count problematic samples
    too_short = (df["text_len"] < 10).sum()
    too_long  = (df["text_len"] > 1000).sum()
    
    print(f"\n🔍 Filtering invalid samples:")
    print(f"   Too short (< 10 chars)  : {too_short}")
    print(f"   Too long  (> 1000 chars): {too_long}")
    
    # ✅ Apply filter
    df = df[
        (df["text_len"] >= 10) &      # Remove very short text
        (df["text_len"] <= 1000)      # Remove abnormally long text
    ].copy()
    
    # Drop temporary column
    df = df.drop(columns=["text_len"])
    
    removed = initial_count - len(df)
    print(f"\n🔧 Filtered out: {removed} samples")
    print(f"   Remaining   : {len(df)} samples")
    
    return df


def validate_dataset(df, label_column):
    """Display dataset statistics"""
    text_lens = df["clean_text"].str.len()
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total samples      : {len(df)}")
    print(f"   Missing values     : {df.isnull().sum().sum()}")
    print(f"   Empty texts        : {(df['clean_text'] == '').sum()}")
    
    print(f"\n📊 Class Distribution:")
    print(df[label_column].value_counts())
    
    print(f"\n📊 Text Length:")
    print(f"   Min   : {text_lens.min()}")
    print(f"   Max   : {text_lens.max()}")
    print(f"   Mean  : {text_lens.mean():.1f}")
    print(f"   Median: {text_lens.median():.1f}")


def split_dataset(df, label_column, test_size=0.15, val_size=0.15):
    """Stratified train/val/test split"""
    train_df, temp_df = train_test_split(
        df,
        test_size=(test_size + val_size),
        stratify=df[label_column],
        random_state=42
    )

    val_df, test_df = train_test_split(
        temp_df,
        test_size=test_size / (test_size + val_size),
        stratify=temp_df[label_column],
        random_state=42
    )

    print(f"\n✅ Split Sizes:")
    print(f"   Train : {len(train_df)}")
    print(f"   Val   : {len(val_df)}")
    print(f"   Test  : {len(test_df)}")

    return train_df, val_df, test_df


def save_splits(train_df, val_df, test_df):
    """Save datasets to CSV"""
    train_df.to_csv("data/processed/train.csv", index=False)
    val_df.to_csv("data/processed/val.csv", index=False)
    test_df.to_csv("data/processed/test.csv", index=False)
    print("\n✅ Splits saved to data/processed/")


if __name__ == "__main__":
    INPUT_PATH   = "data/raw/ambiguity_dataset.csv"
    TEXT_COLUMN  = "sentence"
    LABEL_COLUMN = "is_ambiguous"

    # Step 1: Load and clean
    df = preprocess_dataset(INPUT_PATH, TEXT_COLUMN, LABEL_COLUMN)
    
    # Step 2: ✅ Filter invalid samples (NEW)
    df = filter_invalid_samples(df)
    
    # Step 3: Validate
    validate_dataset(df, LABEL_COLUMN)

    # Step 4: Split
    train_df, val_df, test_df = split_dataset(df, LABEL_COLUMN)
    
    # Step 5: Save
    save_splits(train_df, val_df, test_df)

    print("\n" + "="*50)
    print("✅ PREPROCESSING COMPLETE!")
    print("="*50)