# Scholarship Eligibility Screening System Using Rule-Based Conditions

**BCA Final Year Practical Examination & Viva Project**  
*Technology: Pure Python (Standard Library Only)*  
*Architecture: Deterministic Rule-Based Screening Engine*  

---

## 1. Project Overview

The **Scholarship Eligibility Screening System** is a professional, modular, beginner-friendly Python application that evaluates college scholarship applications from a dataset of 6,607 student records.

Unlike black-box machine learning models or statistical classifiers, this application uses a **deterministic rule-based architecture**. Every scholarship grant or rejection is governed by strict, transparent, and auditable institutional policies, accompanied by clear human-readable explanations.

---

## 2. Official 10-Phase Syllabus Roadmap Alignment

| Phase | Title | Module / Implementation | Status |
|---|---|---|---|
| **Phase 1** | **Dataset Inspection** | `src/inspect_dataset.py` (Kaggle CSV analysis & baseline SHA-256) | Completed |
| **Phase 2** | **Data Loading & Validation** | `src/data_loader.py` & `src/validation.py` (CSV parsing & data integrity gate) | Completed |
| **Phase 3** | **Eligibility Checking** | `src/eligibility.py` (5 Mandatory Threshold Rule Checkers) | Completed |
| **Phase 4** | **Classification Engine** | `src/eligibility.py` (4 Screening Category Tiers) | Completed |
| **Phase 5** | **Eligibility Scoring** | `src/eligibility.py` (`calculate_eligibility_score` out of 100 points) | Completed |
| **Phase 6** | **Ranking System** | `src/ranking.py` (Multi-level `lambda` sorting & tie-breaking) | Completed |
| **Phase 7** | **Report Generation** | `src/report.py` (Summary Text, CSV Screening Log, & Audit Sign-Off) | Completed |
| **Phase 8** | **Menu-Driven Application** | `src/main.py` (Master Interactive Console CLI Application) | Completed |
| **Phase 9** | **Testing** | Automated unit and integration test suites with Python `assert` | Completed |
| **Phase 10** | **Final Documentation** | `README.md`, `requirements.txt`, Viva Voce Examination Guide | Completed |

---

## 3. Key Architectural Principles

- **Zero External Dependencies**: Built 100% with standard Python library modules (`csv`, `os`, `sys`, `datetime`, `hashlib`). No Pandas, NumPy, or external frameworks were used.
- **Dataset Immutability**: The original Kaggle dataset (`dataset/original_dataset.csv`) is treated as read-only and verified using SHA-256 checksums before and after execution.
- **Defensive Data Validation Gate**: Student profiles are verified against strict numerical and category boundaries before entering the screening engine. Invalid records (e.g. out-of-range scores) are disqualified safely.
- **Demonstration Transparency**: Proxy fields created for scholarship evaluation (`Demo_CGPA`, `Demo_Family_Income`, `Demo_Backlogs`, `Demo_Enrollment_Status`) are explicitly labeled as synthetic demonstration data for academic simulation.
- **One-Time In-Memory Caching**: Loads and evaluates all 6,607 records once at startup for instant sub-millisecond menu operations.

---

## 4. Scholarship Rules & Classification Criteria

### Mandatory Eligibility Thresholds
To qualify for any scholarship, a student must satisfy **all 5 mandatory conditions**:
1. **Academic Merit**: `Demo_CGPA >= 7.00` (on an Indian 10.00 scale)
2. **Classroom Attendance**: `Attendance >= 75.0%`
3. **Financial Need**: Annual family income `Demo_Family_Income <= ₹5,00,000`
4. **Academic Backlogs**: `Demo_Backlogs <= 1`
5. **Enrollment Status**: Must be currently `Active`

### Classification Tiers
1. **Highly Eligible**: Meets all mandatory conditions **AND** achieves academic distinction (`Demo_CGPA >= 8.50`) **AND** outstanding attendance (`Attendance >= 85.0%`).
2. **Eligible**: Meets all 5 mandatory conditions under standard thresholds.
3. **Conditionally Eligible (Exception Rule)**: Granted an academic exception if `6.75 <= Demo_CGPA < 7.00`, provided **all other 4 mandatory conditions pass**.
4. **Not Eligible**: Fails one or more critical mandatory conditions.
5. **Invalid Record (Disqualified)**: Failed structural data validation (e.g., `Exam_Score = 101` in row 1526).

---

## 5. Composite Eligibility Scoring Engine (Out of 100 Points)

In addition to categorical classification, the system calculates a multi-factor numerical eligibility score out of 100 points:

| Component | Max Points | Scoring Policy / Formula |
|---|---|---|
| **Academic Merit (CGPA)** | **40 Points** | `(Demo_CGPA / 10.0) * 40.0` |
| **Attendance Performance** | **30 Points** | `(Attendance / 100.0) * 30.0` |
| **Financial Need (Income)** | **20 Points** | Low Income (<= ₹2L) = 20 pts, Medium (<= ₹5L) = 10 pts, High = 0 pts |
| **Merit & Discipline Boost** | **10 Points** | Extracurricular (`Yes`) = 5 pts, Clean Backlogs (`0`) = 5 pts |
| **Total Composite Score** | **100 Points** | Sum of all 4 components (Capped at 100.00) |

*Note: Corrupted or invalid student records (e.g. `STU1526`) receive a safe score of 0.00 to prevent corrupted ranking.*

### Critical Distinction: Merit Rank vs. Informational Score
> **Important Rule:** Rank is by category and tie-breakers; Score is informational.
The 100-point composite score provides a holistic profile summary for advising and student feedback. However, **official institutional merit rank is NEVER decided by the numerical score**. The institutional rank is strictly dictated by:
1. Classification Category Tier (Tier 1: Highly Eligible first $\rightarrow$ Tier 2: Eligible second $\rightarrow$ Tier 3: Conditionally Eligible third)
2. Four-Tier Deterministic Tie-Breakers: `Demo_CGPA` (descending) $\rightarrow$ `Attendance` (descending) $\rightarrow$ `Demo_Family_Income` (ascending) $\rightarrow$ `Student_ID` (ascending alphabetical).

---

## 6. Merit Ranking & Four-Tier Tie-Breaking Protocol

Eligible applicants are ranked within their classification tier using the following strict priority:
1. **Primary Key**: Higher `Demo_CGPA` ranks first (Descending).
2. **1st Tie-Breaker**: Higher `Attendance` ranks first (Descending).
3. **2nd Tie-Breaker**: Lower `Demo_Family_Income` ranks first (Ascending - higher financial need prioritized).
4. **Final Tie-Breaker**: `Student_ID` in ascending alphabetical order (Deterministic consistency).

**Overall Merit Priority Order:**
`Tier 1: Highly Eligible`  $\rightarrow$  `Tier 2: Eligible`  $\rightarrow$  `Tier 3: Conditionally Eligible`

---

## 7. Dataset Statistics & Baseline Metrics

- **Total Records Processed**: 6,607
- **Valid Records**: 6,606 (99.98%)
- **Invalid Records Disqualified**: 1 (0.02% - `STU1526` due to `Exam_Score = 101`)
- **Highly Eligible Scholars**: 7 (0.11%)
- **Eligible Scholars**: 934 (14.14%)
- **Conditionally Eligible Scholars**: 727 (11.00%)
- **Not Eligible Applicants**: 4,938 (74.74%)
- **Total Qualifying Scholars**: 1,668 (25.25%)
- **Dataset SHA-256 Checksum**: `e8df8c4148ef83fb295ca1c092f2c6ee15272c0a8e3018b769a788ab50e96e97`

---

## 8. Project Directory Structure

```text
Scholarship_Eligibility_System/
│
├── dataset/
│   └── original_dataset.csv             # Pristine Kaggle dataset (6,607 rows, SHA-256 verified)
│
├── reports/                             # Timestamped generated reports & audit files
│   ├── scholarship_summary_report_*.txt # Timestamped consolidated ASCII summary report
│   ├── screening_results_*.csv          # Timestamped 6,607 record institutional screening CSV
│   └── screening_audit_report_*.txt     # Timestamped SHA-256 checksum verified audit sign-off
│
├── src/
│   ├── inspect_dataset.py               # Phase 1: Dataset Inspection & Metadata
│   ├── data_loader.py                   # Phase 2: CSV Parsing & Type Preparation
│   ├── validation.py                    # Phase 2: Data Integrity & Range Checking Gate
│   ├── eligibility.py                   # Phases 3-5: Threshold Rules, Classification & Scoring
│   ├── ranking.py                       # Phase 6: Merit Ranking & 4-Tier Tie-Breaking
│   ├── report.py                        # Phase 7: Reporting & Audit File Generation
│   └── main.py                          # Phase 8: Master Interactive Menu-Driven CLI
│
├── README.md                            # Complete Project Documentation & Viva Guide
└── requirements.txt                     # Standard Library Confirmation (Zero dependencies)
```

---

## 9. How to Run the Application

### Launch Master Interactive Application
```powershell
python src/main.py
```

### Interactive Menu Options
```text
========================================
 SCHOLARSHIP ELIGIBILITY SCREENING SYSTEM
========================================

1. Display All Applications
2. Screen Individual Student
3. Screen All Students
4. Search Student
5. Display Eligible Students
6. Display Highly Eligible Students
7. Rank Eligible Students
8. Display Scholarship Summary
9. Display Screening Date and Time
10. Exit

========================================
```

### Running Individual Module Test Suites
You can run any module directly to execute its automated test cases with Python `assert` statements:
```powershell
# Phase 1: Inspect dataset
python src/inspect_dataset.py

# Phase 2: Test data loader & validation gate
python src/data_loader.py
python src/validation.py

# Phases 3, 4, 5: Run eligibility rules, classification & scoring tests
python src/eligibility.py

# Phase 6: Run merit ranking & tie-breaker tests
python src/ranking.py

# Phase 7: Run reporting & audit log tests
python src/report.py
```

---

## 10. Viva Voce & Practical Exam Preparation Q&A

### Q1: Why did you choose a rule-based system instead of a Machine Learning (ML) model?
> **Answer:** Machine Learning models are probabilistic "black-box" systems that can suffer from training bias, unpredictable errors, and a lack of explainability. Scholarship allocation involves legal, ethical, and institutional responsibility. A deterministic rule-based system guarantees 100% transparency, repeatability, and accountability—every applicant receives an exact rule-by-rule justification for why they qualified or failed.

### Q2: Why did you avoid Pandas and NumPy?
> **Answer:** For a core computer science practical exam, using built-in Python modules (`csv`, `os`, `sys`, `datetime`, `hashlib`) demonstrates a fundamental mastery of Python data structures (lists, dictionaries, tuples), algorithmic sorting (multi-level lambda keys), defensive input handling, and standard file I/O, without relying on third-party abstractions.

### Q3: How do you handle tie-breaking when two students have the same CGPA?
> **Answer:** We implemented a 4-tier hierarchical sorting key using `sorted()` with a custom lambda function:
> 1. `-Demo_CGPA` (Descending)
> 2. `-Attendance` (Descending)
> 3. `Demo_Family_Income` (Ascending, giving priority to greater financial need)
> 4. `Student_ID` (Ascending alphabetical, ensuring consistent deterministic output)

### Q4: How does your system verify that the Kaggle dataset was not modified?
> **Answer:** We use Python's built-in `hashlib` module to calculate a SHA-256 cryptographic checksum before and after execution. The baseline hash `e8df8c4148ef83fb295ca1c092f2c6ee15272c0a8e3018b769a788ab50e96e97` is verified to match before any reports claim the dataset is intact.

### Q5: What data anomaly did you find in the Kaggle dataset?
> **Answer:** Row 1526 (`STU1526`) contains an `Exam_Score` of `101`, which exceeds the valid 0–100 scale. Our Phase 2 validation module catches this anomaly at the validation gate, marks the record as `Invalid Record`, and disqualifies it from scholarship evaluation, ensuring corrupt data never skews ranking results.

### Q6: Are Demo_CGPA, Demo_Family_Income, Demo_Backlogs, and Demo_Enrollment_Status real columns from the Kaggle dataset?
> **Answer:** No. The original Kaggle dataset (`StudentPerformanceFactors.csv`) contains study habits and academic performance metrics (e.g. `Hours_Studied`, `Attendance`, `Exam_Score`, and `Family_Income` as High/Medium/Low categories), but lacks college-specific scholarship attributes like 10-point CGPA, numerical annual income, backlog counts, and active enrollment status. In Phase 2, we transparently generate synthetic demonstration proxy fields (`Demo_CGPA` derived from `Exam_Score`, `Demo_Family_Income` mapped from categorical income brackets, `Demo_Backlogs`, and `Demo_Enrollment_Status`) exclusively to simulate institutional scholarship rules without tampering with the original Kaggle CSV file.
