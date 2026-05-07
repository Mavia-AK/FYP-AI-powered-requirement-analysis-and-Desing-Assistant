# AI-RADA Model Results - Poster Summary

## 📊 **Ambiguity Classification Model Performance**

### Overall Test Metrics
- **Accuracy:** 95.96%
- **F1-Score:** 94.64%
- **Precision:** 92.88%
- **Recall:** 96.46%
- **ROC-AUC:** 0.9908

---

## 📈 **Per-Class Performance**

### Clear Requirements
| Metric | Value |
|--------|-------|
| Precision | 97.88% |
| Recall | 95.66% |
| F1-Score | 96.76% |
| Support | 1,060 samples |

### Ambiguous Requirements
| Metric | Value |
|--------|-------|
| Precision | 92.88% |
| Recall | 96.46% |
| F1-Score | 94.64% |
| Support | 622 samples |

---

## 🎯 **Weighted Averages**
- **Weighted Precision:** 96.03%
- **Weighted Recall:** 95.96%
- **Weighted F1-Score:** 95.97%
- **Total Test Samples:** 1,682

---

## 📉 **Training Progress**
- **Final Eval Loss:** 0.233
- **Training Epochs:** 5
- **Total Training Steps:** 600+
- **Eval Runtime:** 64.15 seconds
- **Evaluation Speed:** 26.22 samples/second

---

## 🔍 **Key Highlights**
✅ **Excellent Recall (96.46%)** - Catches almost all ambiguous requirements  
✅ **High Precision (92.88%)** - Minimal false positives  
✅ **Outstanding ROC-AUC (0.9908)** - Excellent class discrimination  
✅ **Balanced Performance** - Strong results on both Clear and Ambiguous classes  

---

## 📋 **Model Configuration**
- **Model Type:** BERT-based Classification
- **Dataset Split:** Training, Validation, Test
- **Evaluation Metric:** F1-Score Optimized
- **Framework:** Hugging Face Transformers

---

## 💾 **Trained Models Location**
- Ambiguity Model: `models/ambiguity/`
- Classification Model: `models/classification_final/`

