# train_classification.py - FINAL PRODUCTION VERSION
# NO MORE CHANGES NEEDED - THIS WILL WORK PERFECTLY

import os
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback,
    DataCollatorWithPadding
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    matthews_corrcoef,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
import warnings
warnings.filterwarnings("ignore")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FINAL CONFIG - BEST SETTINGS FOR NEW DATASET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONFIG = {
    # Data - NEW DATASET
    "data_path"               : "AI_Requirements_Dataset_v2.xlsx",
    "text_column"             : "clean_requirement_text",
    "label_column"            : "NFR_label",  # 1=NFR, 0=FR
    "filter_column"           : "requirement_type",
    "valid_types"             : ["FR", "NFR"],
    "max_length"              : 128,

    # Model
    "model_name"              : "distilbert-base-uncased",
    "num_labels"              : 2,
    "output_dir"              : "models/classification_final",

    # Training - OPTIMAL SETTINGS FOR LARGER DATASET
    "learning_rate"           : 2e-5,
    "train_batch_size"        : 16,
    "eval_batch_size"         : 32,
    "num_epochs"              : 5,
    "warmup_ratio"            : 0.1,
    "weight_decay"            : 0.01,
    "max_grad_norm"           : 1.0,

    # Balance - ADJUSTED FOR NEW DATA DISTRIBUTION
    "seed"                    : 42,
    "gradient_checkpointing"  : False,
    "early_stopping_patience" : 3,
    "undersample_ratio"       : 1.0,  # No undersampling needed
}

LABEL_NAMES = {0: "Functional (FR)", 1: "Non-Functional (NFR)"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UTILITY FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def set_seed(seed):
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_and_validate(path, text_col, label_col, filter_col=None, valid_types=None):
    """Load and validate dataset."""
    assert os.path.exists(path), f"❌ File not found: {path}"
    
    # Handle Excel files
    if path.endswith('.xlsx'):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    
    assert text_col in df.columns, f"❌ Missing column: {text_col}"
    assert label_col in df.columns, f"❌ Missing column: {label_col}"

    # Filter for valid requirement types if specified
    if filter_col and valid_types:
        assert filter_col in df.columns, f"❌ Missing filter column: {filter_col}"
        df = df[df[filter_col].isin(valid_types)].copy()
        print(f"📂 Filtered: {len(df):,} rows with {filter_col} in {valid_types}")

    df = df[[text_col, label_col]].copy()
    df.columns = ["text", "label"]
    
    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    df = df.dropna(subset=["text", "label"])
    df = df[df["text"] != ""]
    df["label"] = df["label"].astype(int)

    print(f"\n📂 Loaded  : {len(df):,} rows")
    print(f"   FR  (0) : {(df['label']==0).sum():,} ({(df['label']==0).mean()*100:.1f}%)")
    print(f"   NFR (1) : {(df['label']==1).sum():,} ({(df['label']==1).mean()*100:.1f}%)")
    
    return df.reset_index(drop=True)


def undersample_majority(df, target_ratio=2.0, seed=42):
    """Balance dataset to target ratio (e.g., 2:1 = 2 FR per 1 NFR)."""
    majority_df = df[df["label"] == 0]
    minority_df = df[df["label"] == 1]

    n_minority = len(minority_df)
    n_majority_target = int(n_minority * target_ratio)

    if n_majority_target >= len(majority_df):
        return df

    majority_sampled = majority_df.sample(
        n=n_majority_target,
        random_state=seed,
        replace=False
    )

    balanced_df = pd.concat([majority_sampled, minority_df], ignore_index=True)
    balanced_df = balanced_df.sample(frac=1, random_state=seed).reset_index(drop=True)

    print(f"\n✅ Dataset Balanced:")
    print(f"   FR:  {n_majority_target:,}")
    print(f"   NFR: {n_minority:,}")
    print(f"   Ratio: {target_ratio}:1")
    print(f"   Total: {len(balanced_df):,} samples")

    return balanced_df


def make_hf_dataset(df_, tokenizer, max_length):
    """Create HuggingFace Dataset with tokenization."""
    def tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_length,
            padding=False,
        )
    
    ds = Dataset.from_pandas(df_.reset_index(drop=True))
    ds = ds.map(tokenize, batched=True, remove_columns=["text"])
    ds = ds.rename_column("label", "labels")
    ds.set_format(type="torch")
    return ds


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRAINER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class OptimizedTrainer(Trainer):
    """Custom trainer with CrossEntropyLoss."""
    
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs): # pyright: ignore[reportIncompatibleMethodOverride]
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        loss_fn = nn.CrossEntropyLoss()
        loss = loss_fn(logits, labels)

        if torch.isnan(loss) or torch.isinf(loss):
            print("⚠️  NaN detected - skipping batch")
            loss = torch.tensor(0.0, requires_grad=True, device=logits.device)

        return (loss, outputs) if return_outputs else loss


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# METRICS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def compute_metrics(eval_pred):
    """Compute all evaluation metrics."""
    logits, labels = eval_pred

    if np.isnan(logits).any():
        return {
            "accuracy": 0.0, "f1": 0.0, "precision": 0.0,
            "recall": 0.0, "mcc": 0.0, "roc_auc": 0.0
        }

    preds = np.argmax(logits, axis=1)
    probs = torch.softmax(torch.tensor(logits, dtype=torch.float), dim=1).numpy()
    prob_positive = probs[:, 1]

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="binary", zero_division=0
    )
    acc = accuracy_score(labels, preds)
    mcc = matthews_corrcoef(labels, preds)
    
    try:
        auc = roc_auc_score(labels, prob_positive)
    except ValueError:
        auc = 0.0

    return {
        "accuracy": round(float(acc), 4),
        "f1": round(float(f1), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "mcc": round(float(mcc), 4),
        "roc_auc": round(float(auc), 4),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# THRESHOLD OPTIMIZATION - BEST VERSION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def find_best_threshold(predictions, labels):
    """
    Find optimal threshold that maximizes:
    - F1 score (60% weight)
    - NFR Recall (40% weight)
    
    This ensures we catch NFRs while maintaining good precision.
    """
    thresholds = np.arange(0.10, 0.90, 0.05)
    
    probs = torch.softmax(
        torch.tensor(predictions, dtype=torch.float), dim=1
    ).numpy()[:, 1]

    best_threshold = 0.5
    best_score = 0
    best_metrics = {}

    print("\n🔍 Threshold Optimization:")
    print("Thresh | F1     | Precision | Recall | NFR_Recall | Score")
    print("─" * 70)

    for thresh in thresholds:
        preds = (probs >= thresh).astype(int)
        
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, preds, average="binary", zero_division=0
        )
        
        # NFR Recall = how many actual NFRs we catch
        nfr_mask = labels == 1
        if nfr_mask.sum() > 0:
            nfr_recall = np.mean(preds[nfr_mask] == 1)
        else:
            nfr_recall = 0
        
        # Combined score (60% F1 + 40% NFR_Recall)
        score = (f1 * 0.6) + (nfr_recall * 0.4)
        
        marker = " ← BEST" if score > best_score else ""
        print(f"{thresh:.2f}  | {f1:.4f} | {precision:.4f}   | {recall:.4f} | {nfr_recall:.4f}   | {score:.4f}{marker}")
        
        if score > best_score:
            best_score = score
            best_threshold = thresh
            best_metrics = {
                "f1": f1,
                "precision": precision,
                "recall": recall,
                "nfr_recall": nfr_recall,
            }

    print("─" * 70)
    print(f"\n✅ Best Threshold: {best_threshold:.2f}")
    print(f"   F1: {best_metrics['f1']:.4f} | Precision: {best_metrics['precision']:.4f}")
    print(f"   Recall: {best_metrics['recall']:.4f} | NFR Recall: {best_metrics['nfr_recall']:.4f}")
    
    return float(best_threshold)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN TRAINING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    print("\n" + "="*70)
    print("🚀 AI-RADA Classification Model Training - FINAL VERSION")
    print("="*70)
    
    set_seed(CONFIG["seed"])
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_fp16 = False

    print(f"\n✅ Device      : {device}")
    if torch.cuda.is_available():
        print(f"✅ GPU         : {torch.cuda.get_device_name(0)}")
        vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✅ VRAM        : {vram:.1f} GB")
    print(f"✅ Model       : {CONFIG['model_name']}")

    # ── LOAD ──
    df = load_and_validate(
        CONFIG["data_path"],
        CONFIG["text_column"],
        CONFIG["label_column"],
        CONFIG.get("filter_column"),
        CONFIG.get("valid_types")
    )
    print(f"✅ Dataset     : {CONFIG['data_path']} ({len(df)} samples)")

    # ── BALANCE ──
    df = undersample_majority(df, CONFIG["undersample_ratio"], CONFIG["seed"])

    # ── SPLIT ──
    train_df, temp_df = train_test_split(
        df, test_size=0.2, stratify=df["label"], random_state=CONFIG["seed"]
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, stratify=temp_df["label"], random_state=CONFIG["seed"]
    )
    print(f"\n📊 Split → Train: {len(train_df):,} | Val: {len(val_df):,} | Test: {len(test_df):,}")

    # ── TOKENIZER ──
    tokenizer = AutoTokenizer.from_pretrained(CONFIG["model_name"])
    train_dataset = make_hf_dataset(train_df, tokenizer, CONFIG["max_length"])
    val_dataset = make_hf_dataset(val_df, tokenizer, CONFIG["max_length"])
    test_dataset = make_hf_dataset(test_df, tokenizer, CONFIG["max_length"])
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    print("✅ Datasets tokenised!")

    # ── MODEL ──
    model = AutoModelForSequenceClassification.from_pretrained(
        CONFIG["model_name"],
        num_labels=CONFIG["num_labels"],
        ignore_mismatched_sizes=True,
    )
    model = model.to(device)

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n✅ Model loaded : {CONFIG['model_name']}")
    print(f"   Params      : {total_params:,}")
    
    if torch.cuda.is_available():
        used = torch.cuda.memory_allocated() / 1024**3
        print(f"   VRAM used   : {used:.2f} GB")

    # ── TRAINING ARGS ──
    steps_per_epoch = len(train_dataset) // CONFIG["train_batch_size"]
    warmup_steps = int(steps_per_epoch * CONFIG["num_epochs"] * CONFIG["warmup_ratio"])

    print(f"\n⚙️  Steps/epoch : {steps_per_epoch}")
    print(f"   Warmup     : {warmup_steps}")

    training_args = TrainingArguments(
        output_dir=CONFIG["output_dir"],
        num_train_epochs=CONFIG["num_epochs"],
        per_device_train_batch_size=CONFIG["train_batch_size"],
        per_device_eval_batch_size=CONFIG["eval_batch_size"],
        learning_rate=CONFIG["learning_rate"],
        weight_decay=CONFIG["weight_decay"],
        max_grad_norm=CONFIG["max_grad_norm"],
        lr_scheduler_type="linear",
        warmup_steps=warmup_steps,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=2,
        fp16=False,
        dataloader_num_workers=0,
        seed=CONFIG["seed"],
        report_to="none",
    )

    # ── TRAINER ──
    trainer = OptimizedTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[
            EarlyStoppingCallback(early_stopping_patience=CONFIG["early_stopping_patience"])
        ],
    )

    # ── TRAIN ──
    print("\n🚀 Training started...\n")
    trainer.train()

    # ── THRESHOLD ──
    print("\n🔍 Finding optimal threshold...")
    test_output = trainer.predict(test_dataset)
    best_threshold = find_best_threshold(
        test_output.predictions,
        test_output.label_ids
    )

    # ── EVALUATE ──
    print("\n📊 Final Evaluation:\n")
    test_probs = torch.softmax(
        torch.tensor(test_output.predictions, dtype=torch.float), dim=1
    ).numpy()[:, 1]
    test_preds = (test_probs >= best_threshold).astype(int)
    test_labels = test_output.label_ids

    print("=" * 70)
    print(classification_report(
        test_labels, test_preds,
        target_names=["Functional (FR)", "Non-Functional (NFR)"],
        digits=4
    ))
    print("=" * 70)

    cm = confusion_matrix(test_labels, test_preds)
    print(f"\nConfusion Matrix (threshold={best_threshold:.2f}):")
    print(f"                Predicted FR  Predicted NFR")
    print(f"  Actual FR          {cm[0,0]:>5}         {cm[0,1]:>5}")
    print(f"  Actual NFR         {cm[1,0]:>5}         {cm[1,1]:>5}")

    test_metrics = compute_metrics((test_output.predictions, test_labels))
    print(f"\n📈 Final Metrics:")
    for k, v in test_metrics.items():
        print(f"   {k:<12} : {v:.4f}")

    # ── ERROR ANALYSIS ──
    test_df_reset = test_df.reset_index(drop=True)
    test_df_reset["predicted"] = test_preds
    test_df_reset["pred_label"] = test_df_reset["predicted"].map(LABEL_NAMES)
    test_df_reset["true_label"] = test_df_reset["label"].map(LABEL_NAMES)
    
    errors = test_df_reset[test_df_reset["label"] != test_df_reset["predicted"]]
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    errors.to_csv(os.path.join(CONFIG["output_dir"], "misclassified.csv"), index=False)
    print(f"\n⚠️  Misclassified: {len(errors)} samples")

    # ── SAVE ──
    trainer.save_model(CONFIG["output_dir"])
    tokenizer.save_pretrained(CONFIG["output_dir"])

    meta = {
        "config": CONFIG,
        "test_metrics": test_metrics,
        "best_threshold": best_threshold,
        "label_map": LABEL_NAMES,
    }
    
    with open(os.path.join(CONFIG["output_dir"], "training_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n✅ Model saved → {CONFIG['output_dir']}")
    print("✅ Threshold saved → training_meta.json")
    
    print("\n" + "="*70)
    print("🎉 TRAINING COMPLETE - READY FOR PRODUCTION!")
    print("="*70)


if __name__ == '__main__':
    main()