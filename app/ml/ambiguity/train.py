import json
import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import seaborn as sns

from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding,
    EarlyStoppingCallback
)
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
    roc_auc_score,
    roc_curve,
    auc
)
import scipy.special

# ─────────────────────────────────────────────
# 🔹 Create Folders
# ─────────────────────────────────────────────
os.makedirs("evaluation", exist_ok=True)
os.makedirs("models/ambiguity", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ─────────────────────────────────────────────
# 🔹 Device
# ─────────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"✅ Using device: {device}")

# ─────────────────────────────────────────────
# 🔹 Load Data
# ─────────────────────────────────────────────
train_df = pd.read_csv("data/processed/train.csv")
val_df   = pd.read_csv("data/processed/val.csv")
test_df  = pd.read_csv("data/processed/test.csv")

print(f"\n📊 Dataset Summary:")
print(f"  Train samples : {len(train_df)}")
print(f"  Val samples   : {len(val_df)}")
print(f"  Test samples  : {len(test_df)}")

# ─────────────────────────────────────────────
# 🔹 Class Weights (Clamped)
# ─────────────────────────────────────────────
class_counts = train_df["is_ambiguous"].value_counts().sort_index()
total        = len(train_df)

weight_0 = total / (2 * class_counts[0])
weight_1 = total / (2 * class_counts[1])

# ✅ Clamp weights to prevent training instability
weight_0 = min(weight_0, 1.2)
weight_1 = min(weight_1, 1.2)

class_weights = torch.tensor(
    [weight_0, weight_1],
    dtype=torch.float32
).to(device)

print(f"\n📊 Class Distribution (Train):")
print(f"  Class 0 (Clear)     : {class_counts[0]}")
print(f"  Class 1 (Ambiguous) : {class_counts[1]}")
print(f"\n📊 Class Weights (Clamped ≤ 1.2):")
print(f"  Weight 0 : {weight_0:.4f}")
print(f"  Weight 1 : {weight_1:.4f}")

# ─────────────────────────────────────────────
# 🔹 Model Name
# ─────────────────────────────────────────────
MODEL_NAME = "microsoft/deberta-v3-base"

# ─────────────────────────────────────────────
# 🔹 Tokenizer
# ─────────────────────────────────────────────
print(f"\n🔄 Loading tokenizer: {MODEL_NAME}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(example):
    return tokenizer(
        example["clean_text"],
        truncation=True,
        max_length=256
    )

# ─────────────────────────────────────────────
# 🔹 Prepare Dataset
# ─────────────────────────────────────────────
def prepare_dataset(df: pd.DataFrame) -> Dataset:
    """Convert DataFrame to tokenized HuggingFace Dataset."""
    df = df.reset_index(drop=True)

    hf_dataset = Dataset.from_pandas(df)

    hf_dataset = hf_dataset.map(
        tokenize_function,
        batched=True,
        desc="Tokenizing"
    )

    hf_dataset = hf_dataset.rename_column("is_ambiguous", "label")

    hf_dataset = hf_dataset.map(
        lambda x: {"label": int(x["label"])},
        desc="Casting labels"
    )

    hf_dataset.set_format(
        type="torch",
        columns=["input_ids", "attention_mask", "label"]
    )

    return hf_dataset  # type: ignore[return-value]


print("\n🔄 Preparing datasets...")
train_dataset = prepare_dataset(train_df)
val_dataset   = prepare_dataset(val_df)
test_dataset  = prepare_dataset(test_df)
print("✅ Datasets ready!")

# ─────────────────────────────────────────────
# 🔹 Model
# ─────────────────────────────────────────────
print(f"\n🔄 Loading model: {MODEL_NAME}")
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2,
    hidden_dropout_prob=0.1,
    attention_probs_dropout_prob=0.1
).to(device)

# ✅ CRITICAL FIX: Force FP32 to prevent NaN gradients
model = model.float()

print("✅ Model loaded!")
print(f"   Model dtype: {next(model.parameters()).dtype}")

# ─────────────────────────────────────────────
# 🔹 Data Collator
# ─────────────────────────────────────────────
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# ─────────────────────────────────────────────
# 🔹 Metrics (Research Level)
# ─────────────────────────────────────────────
def compute_metrics(eval_pred):
    logits, labels = eval_pred

    if isinstance(logits, tuple):
        logits = logits[0]

    predictions = np.argmax(logits, axis=1)

    # Probabilities for ROC-AUC
    probabilities = scipy.special.softmax(logits, axis=1)[:, 1]

    # Core metrics
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels,
        predictions,
        average="binary",
        zero_division=0
    )
    acc = accuracy_score(labels, predictions)

    # ROC-AUC
    try:
        roc_auc = roc_auc_score(labels, probabilities)
    except ValueError:
        roc_auc = 0.0

    return {
        "accuracy"  : round(float(acc), 4),
        "f1"        : round(float(f1), 4),
        "precision" : round(float(precision), 4),
        "recall"    : round(float(recall), 4),
        "roc_auc"   : round(float(roc_auc), 4),
    }

# ─────────────────────────────────────────────
# 🔹 Custom Weighted Trainer
# ─────────────────────────────────────────────
class WeightedTrainer(Trainer):
    """
    Custom Trainer with class-weighted CrossEntropyLoss.
    Handles dtype mismatches automatically.
    """

    def compute_loss(
        self,
        model,
        inputs,
        return_outputs: bool = False,
        num_items_in_batch=None,
    ):
        labels  = inputs.get("labels")
        outputs = model(**inputs)
        logits  = outputs.get("logits")

        if logits is None:
            raise ValueError("Model did not return logits.")
        if labels is None:
            raise ValueError("Labels not found in inputs.")

        # ✅ Match dtype dynamically
        weights  = class_weights.to(dtype=logits.dtype, device=logits.device)
        loss_fct = nn.CrossEntropyLoss(weight=weights)
        loss     = loss_fct(
            logits.view(-1, 2),
            labels.view(-1)
        )

        return (loss, outputs) if return_outputs else loss

# ─────────────────────────────────────────────
# 🔹 Training Steps Calculation
# ─────────────────────────────────────────────
BATCH_SIZE   = 12
NUM_EPOCHS   = 5

total_steps  = (len(train_df) // BATCH_SIZE) * NUM_EPOCHS
warmup_steps = int(total_steps * 0.1)

print(f"\n📊 Training Config:")
print(f"  Batch size   : {BATCH_SIZE}")
print(f"  Epochs       : {NUM_EPOCHS}")
print(f"  Total steps  : {total_steps}")
print(f"  Warmup steps : {warmup_steps}")

# ─────────────────────────────────────────────
# 🔹 Training Arguments
# ─────────────────────────────────────────────
training_args = TrainingArguments(
    output_dir="models/ambiguity",

    # Learning
    learning_rate=1e-5,
    weight_decay=0.01,
    warmup_steps=warmup_steps,
    max_grad_norm=0.5,

    # Batch & Epochs
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=16,
    num_train_epochs=NUM_EPOCHS,

    # Evaluation & Saving
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_strategy="steps",
    logging_steps=100,

    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    save_total_limit=2,

    # Precision (disabled for stability)
    fp16=False,
    bf16=False,

    # Misc
    report_to="none",
    seed=42,
    dataloader_num_workers=0,
)

# ─────────────────────────────────────────────
# 🔹 Trainer
# ─────────────────────────────────────────────
trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,       # type: ignore[arg-type]
    eval_dataset=val_dataset,          # type: ignore[arg-type]
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    callbacks=[
        EarlyStoppingCallback(early_stopping_patience=2)
    ],
)

# ─────────────────────────────────────────────
# 🔹 Train
# ─────────────────────────────────────────────
print("\n🚀 Starting Training...")
print("="*50)
trainer.train()
print("="*50)

# ─────────────────────────────────────────────
# 🔹 Save Model & Tokenizer
# ─────────────────────────────────────────────
trainer.save_model("models/ambiguity")
tokenizer.save_pretrained("models/ambiguity")
print("\n✅ Model & tokenizer saved!")

# ─────────────────────────────────────────────
# 🔹 Evaluate on Test Set
# ─────────────────────────────────────────────
print("\n📊 Evaluating on test set...")
test_results = trainer.evaluate(test_dataset)  # type: ignore[arg-type]

print("\n📋 Test Results:")
print("="*40)
for key, value in test_results.items():
    print(f"  {key}: {value}")
print("="*40)

with open("evaluation/ambiguity_test_results.json", "w") as f:
    json.dump(test_results, f, indent=2)
print("✅ Test results saved!")

# ─────────────────────────────────────────────
# 🔹 Predictions
# ─────────────────────────────────────────────
print("\n📊 Generating predictions on test set...")
pred_output = trainer.predict(test_dataset)  # type: ignore[arg-type]

raw_logits = pred_output.predictions
if isinstance(raw_logits, tuple):
    raw_logits = raw_logits[0]

y_true_raw = pred_output.label_ids
if y_true_raw is None:
    raise ValueError("label_ids is None — check test dataset labels.")

y_true: np.ndarray = np.array(y_true_raw)
y_pred: np.ndarray = np.array(np.argmax(raw_logits, axis=1))
y_prob: np.ndarray = scipy.special.softmax(raw_logits, axis=1)[:, 1]

# ─────────────────────────────────────────────
# 🔹 Classification Report
# ─────────────────────────────────────────────
print("\n📋 Classification Report:")
print("="*50)
print(classification_report(
    y_true,
    y_pred,
    target_names=["Clear", "Ambiguous"],
    zero_division=0
))

report_dict = classification_report(
    y_true,
    y_pred,
    target_names=["Clear", "Ambiguous"],
    output_dict=True,
    zero_division=0
)
with open("evaluation/ambiguity_classification_report.json", "w") as f:
    json.dump(report_dict, f, indent=2)
print("✅ Classification report saved!")

# ─────────────────────────────────────────────
# 🔹 Confusion Matrix
# ─────────────────────────────────────────────
cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Clear", "Ambiguous"],
    yticklabels=["Clear", "Ambiguous"],
)
plt.title("Ambiguity Detection — Confusion Matrix", fontsize=14, fontweight="bold")
plt.ylabel("True Label", fontsize=12)
plt.xlabel("Predicted Label", fontsize=12)
plt.tight_layout()
plt.savefig("evaluation/confusion_matrix_ambiguity.png", dpi=150)
plt.close()
print("✅ Confusion matrix saved!")

# ─────────────────────────────────────────────
# 🔹 ROC Curve
# ─────────────────────────────────────────────
fpr, tpr, _ = roc_curve(y_true, y_prob)
roc_auc     = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(
    fpr, tpr,
    color="darkorange",
    lw=2,
    label=f"ROC curve (AUC = {roc_auc:.4f})"
)
plt.plot([0, 1], [0, 1], color="navy", lw=1, linestyle="--")
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel("False Positive Rate", fontsize=12)
plt.ylabel("True Positive Rate", fontsize=12)
plt.title("Ambiguity Detection — ROC Curve", fontsize=14, fontweight="bold")
plt.legend(loc="lower right")
plt.grid(True)
plt.tight_layout()
plt.savefig("evaluation/roc_curve_ambiguity.png", dpi=150)
plt.close()
print(f"✅ ROC curve saved! AUC = {roc_auc:.4f}")

# ─────────────────────────────────────────────
# 🔹 Training History & Curves
# ─────────────────────────────────────────────
history = trainer.state.log_history
with open("evaluation/training_history.json", "w") as f:
    json.dump(history, f, indent=2)
print("✅ Training history saved!")

train_loss = [x["loss"] for x in history if "loss" in x and "eval_loss" not in x]
eval_loss  = [x["eval_loss"] for x in history if "eval_loss" in x]
eval_f1    = [x["eval_f1"] for x in history if "eval_f1" in x]
eval_acc   = [x["eval_accuracy"] for x in history if "eval_accuracy" in x]
eval_auc   = [x["eval_roc_auc"] for x in history if "eval_roc_auc" in x]

if train_loss and eval_loss:
    fig, axes = plt.subplots(1, 4, figsize=(22, 5))

    # Loss
    axes[0].plot(range(1, len(eval_loss)+1), train_loss[:len(eval_loss)],
                 label="Train Loss", marker="o", color="blue")
    axes[0].plot(range(1, len(eval_loss)+1), eval_loss,
                 label="Val Loss", marker="o", color="orange")
    axes[0].set_title("Loss Curve", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].legend()
    axes[0].grid(True)

    # F1
    axes[1].plot(range(1, len(eval_f1)+1), eval_f1,
                 label="Val F1", marker="o", color="green")
    axes[1].set_title("F1 Score", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("F1 Score")
    axes[1].legend()
    axes[1].grid(True)

    # Accuracy
    axes[2].plot(range(1, len(eval_acc)+1), eval_acc,
                 label="Val Accuracy", marker="o", color="purple")
    axes[2].set_title("Accuracy", fontsize=12, fontweight="bold")
    axes[2].set_xlabel("Epoch")
    axes[2].set_ylabel("Accuracy")
    axes[2].legend()
    axes[2].grid(True)

    # ROC-AUC
    if eval_auc:
        axes[3].plot(range(1, len(eval_auc)+1), eval_auc,
                     label="Val ROC-AUC", marker="o", color="red")
        axes[3].set_title("ROC-AUC", fontsize=12, fontweight="bold")
        axes[3].set_xlabel("Epoch")
        axes[3].set_ylabel("AUC Score")
        axes[3].legend()
        axes[3].grid(True)

    plt.suptitle(
        "Ambiguity Detection — Training Curves",
        fontsize=15, fontweight="bold"
    )
    plt.tight_layout()
    plt.savefig("evaluation/training_curves_ambiguity.png", dpi=150)
    plt.close()
    print("✅ Training curves saved!")

# ─────────────────────────────────────────────
# 🔹 Final Summary
# ─────────────────────────────────────────────
print("\n" + "="*50)
print("✅ TRAINING COMPLETE — FINAL RESULTS")
print("="*50)
print(f"  Accuracy  : {test_results.get('eval_accuracy',  'N/A')}")
print(f"  F1        : {test_results.get('eval_f1',        'N/A')}")
print(f"  Precision : {test_results.get('eval_precision', 'N/A')}")
print(f"  Recall    : {test_results.get('eval_recall',    'N/A')}")
print(f"  ROC-AUC   : {test_results.get('eval_roc_auc',   'N/A')}")
print("="*50)
print("\n📁 Saved Files:")
print("  models/ambiguity/")
print("  evaluation/ambiguity_test_results.json")
print("  evaluation/ambiguity_classification_report.json")
print("  evaluation/confusion_matrix_ambiguity.png")
print("  evaluation/roc_curve_ambiguity.png")
print("  evaluation/training_curves_ambiguity.png")
print("  evaluation/training_history.json")
print("="*50)