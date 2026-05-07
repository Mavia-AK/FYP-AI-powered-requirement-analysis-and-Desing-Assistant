# AI-RADA Dataset Details - Poster Information

## 📊 **Dataset Overview**

### Raw Dataset Statistics
- **Total Samples:** 11,440 Requirements
- **Total Features:** 9 columns
- **Missing Values:** 0 (Complete dataset)
- **Data Quality:** 100% complete

---

## 🏷️ **Raw Dataset Composition**

### Ambiguity Type Distribution
| Ambiguity Type | Samples | Percentage |
|---|---|---|
| Unambiguous | 7,284 | 63.7% |
| Weak Modal | 2,154 | 18.8% |
| Missing Actor | 859 | 7.5% |
| Vague | 802 | 7.0% |
| Incomplete | 340 | 3.0% |
| Negation | 1 | 0.01% |
| **Total** | **11,440** | **100%** |

---

## 📁 **Processed Dataset Split**

### Overall Split
- **Total Preprocessed Samples:** 11,213
- **Training Set:** 7,849 samples (70.0%)
- **Validation Set:** 1,682 samples (15.0%)
- **Test Set:** 1,682 samples (15.0%)

---

### Training Set
| Class | Samples | Percentage |
|---|---|---|
| Clear (0) | 4,943 | 63.0% |
| Ambiguous (1) | 2,906 | 37.0% |
| **Total** | **7,849** | **100%** |

### Validation Set
| Class | Samples | Percentage |
|---|---|---|
| Clear (0) | 1,059 | 63.0% |
| Ambiguous (1) | 623 | 37.0% |
| **Total** | **1,682** | **100%** |

### Test Set
| Class | Samples | Percentage |
|---|---|---|
| Clear (0) | 1,060 | 63.0% |
| Ambiguous (1) | 622 | 37.0% |
| **Total** | **1,682** | **100%** |

---

## 🔍 **Feature Details**

### Raw Dataset Features (9 columns)
1. **id** - Unique requirement identifier
2. **sentence** - Requirement text
3. **security** - Security requirement indicator (binary)
4. **reliability** - Reliability requirement indicator (binary)
5. **NFR_boolean** - Non-functional requirement flag (binary)
6. **ambiguity_score** - Numerical ambiguity score
7. **ambiguity_flags** - Categorical ambiguity indicators
8. **is_ambiguous** - Binary ambiguity label
9. **ambiguity_type** - Categorical ambiguity classification

### Processed Dataset Features (3 columns)
1. **clean_text** - Preprocessed requirement text
2. **clean_text_baseline** - Baseline cleaned text
3. **is_ambiguous** - Binary classification label (0=Clear, 1=Ambiguous)

---

## 🎯 **Data Characteristics**

### Class Balance
- **Balanced Distribution:** ~63% Clear vs ~37% Ambiguous requirements
- **Consistent across splits:** Train/Val/Test maintain same ratio
- **No class imbalance issues:** Well-distributed for training

### Data Quality
✅ **Zero missing values** - Complete dataset  
✅ **Consistent splits** - Same class distribution across train/val/test  
✅ **Preprocessed text** - Cleaned and tokenized  
✅ **Stratified sampling** - Maintains class proportions  

---

## 📈 **Dataset Statistics**

| Metric | Value |
|--------|-------|
| Raw Dataset | 11,440 samples |
| Preprocessed Dataset | 11,213 samples |
| Data Retention | 98.0% |
| Number of Features (Raw) | 9 |
| Number of Features (Processed) | 3 |
| Total Train/Val/Test | 11,213 |
| Train/Val/Test Ratio | 70:15:15 |
| Class Categories | 2 (Clear/Ambiguous) |
| Ambiguity Types (Raw) | 6 types |

---

## 🔬 **Preprocessing Pipeline**

### Data Transformation Steps
1. **Loading** - Read raw CSV with 11,440 requirements
2. **Cleaning** - Remove noise and standardize text
3. **Tokenization** - Convert text to tokens
4. **Feature Extraction** - Generate clean_text and clean_text_baseline
5. **Labeling** - Binary ambiguity classification (0 or 1)
6. **Splitting** - Train/Val/Test split (70:15:15)
7. **Validation** - Ensure class balance and data integrity

### Data Sources
- **Raw Data:** `data/raw/ambiguity_dataset.csv`
- **Processed Data:** `data/processed/` (train.csv, val.csv, test.csv)

---

## 📋 **Dataset Summary**

**AI-RADA Ambiguity Classification Dataset**

- **Domain:** Software Requirements Engineering
- **Task:** Binary Ambiguity Classification
- **Total Samples:** 11,213 (after preprocessing)
- **Original Samples:** 11,440 (raw data)
- **Data Quality:** 100% complete, no missing values
- **Class Distribution:** 63% Clear, 37% Ambiguous
- **Input:** Text requirements
- **Output:** Binary classification label
- **Format:** CSV files with preprocessing metadata

---

## 🎓 **Key Points for Poster**

✨ **11,440 real-world software requirements**  
✨ **100% data quality - no missing values**  
✨ **Carefully balanced dataset (63:37 split)**  
✨ **Professional preprocessing pipeline**  
✨ **Stratified train/val/test split (70:15:15)**  
✨ **6 types of ambiguity analyzed**  
✨ **Ready for deep learning models**  

