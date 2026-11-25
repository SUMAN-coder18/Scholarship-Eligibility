# Scholarship Eligibility Screening System Using Rule-Based Conditions

**BCA 2nd Year Practical ExaminationCapstone Project**  
*Technology Stack: Python 3.14 (Pure Standard Library: csv, os, sys, datetime, hashlib)*  
*Architecture: Deterministic Rule-Based Screening Engine & Interactive Console Application*  
*GitHub Repository: [SUMAN-coder18/Scholarship-Eligibility](https://github.com/SUMAN-coder18/Scholarship-Eligibility)*  

---

## 1. Project Overview

The **Scholarship Eligibility Screening System** is an end-to-end, modular, fully transparent academic software system designed to automate institutional scholarship evaluations for higher education colleges and universities.

Using a real-world dataset of **6,607 student records** (derived from Kaggle's *Student Performance Factors*), the system evaluates student profiles against five mandatory institutional criteria, calculates multi-factor composite scores, groups candidates into standardized eligibility tiers, applies strict four-level tie-breaking merit ranking, generates official timestamped compliance audit documents, and presents the entire workflow through a high-performance **Interactive Console Application (`src/main.py`)**.

Unlike probabilistic machine learning classifiers or black-box algorithms, this application is **100% deterministic and rule-based**. Every scholarship decision is auditable, repeatable, mathematically explainable, and accompanied by transparent rule-by-rule justification.

---

## 2. Key Highlights & Distinguishing Features

- **Pure Python Standard Library (Zero External Dependencies)**: Runs on any standard Python installation without installing pip packages (no Pandas, NumPy, or web servers required).
- **Interactive Menu-Driven Console CLI**: Fast terminal interface with defensive input validation, substring search, pagination, individual student evaluation, merit ranking, and report generation.
- **Python as Single Source of Truth**: All screening rules, scores, and rankings are calculated deterministically by core Python modules in `src/`.
- **Dataset Immutability & SHA-256 Verification**: The Kaggle dataset is strictly read-only. Integrity is cryptographically verified against the golden hash: `e8df8c4148ef83fb295ca1c092f2c6ee15272c0a8e3018b769a788ab50e96e97`.
- **Defensive Data Validation Gate**: Catches corrupt data (e.g. `STU1526` with `Exam_Score = 101`) before evaluation, safely disqualifying invalid records without crashing.
- **Transparent Demonstration Proxies**: All derived scholarship simulation fields (`Demo_CGPA`, `Demo_Family_Income`, `Demo_Backlogs`, `Demo_Enrollment_Status`) are clearly labeled and disclosed for college viva evaluation.

---

## 3. Official 10-Phase Syllabus Roadmap Alignment

| Phase | Title | Module / Implementation | Description |
|---|---|---|---|
| **Phase 1** | **Dataset Inspection** | `src/inspect_dataset.py` | Kaggle CSV structure analysis, column schema audit, and baseline SHA-256 computation. |
| **Phase 2** | **Data Loading & Validation** | `src/data_loader.py` & `src/validation.py` | CSV parsing, type casting, synthetic proxy preparation, and 10-rule integrity gate. |
| **Phase 3** | **Eligibility Checking** | `src/eligibility.py` | 5 mandatory threshold rule checkers (CGPA, Attendance, Income, Backlogs, Enrollment). |
| **Phase 4** | **Classification Engine** | `src/eligibility.py` | Assignment into 4 standardized tiers: Highly Eligible, Eligible, Conditionally Eligible, Not Eligible. |
| **Phase 5** | **Eligibility Scoring** | `src/eligibility.py` | 100-point composite scoring engine (Academic /40, Attendance /30, Income /20, Merit Boost /10). |
| **Phase 6** | **Ranking System** | `src/ranking.py` | Category tier ranking and 4-tier deterministic tie-breaking using multi-key lambda expressions. |
| **Phase 7** | **Report Generation** | `src/report.py` | Automated export of timestamped Text Summaries, 6,607-row CSV Datasets, and SHA-256 Audit Logs. |
| **Phase 8** | **Menu-Driven Application** | `src/main.py` | Master interactive console CLI with defensive input handling and pagination. |
| **Phase 9** | **Testing & Verification** | Test suites in all modules | Automated unit, integration, and assertion tests for all valid, invalid, and boundary cases. |
| **Phase 10** | **Project Documentation** | `README.md` & `Project_Report_BWU.md` | Complete university examination report and viva voce documentation. |

---

## 4. Scholarship Rules & Classification Criteria

### Mandatory Eligibility Thresholds
To qualify for institutional scholarships, applicants must satisfy **all 5 mandatory conditions**:

1. **Academic Performance**: `Demo_CGPA >= 7.00` (on a 10.00 scale)
2. **Classroom Attendance**: `Attendance >= 75.0%`
3. **Financial Need**: Annual family income `Demo_Family_Income <= ₹5,00,000`
4. **Disciplinary & Backlogs Limit**: `Demo_Backlogs <= 1`
5. **Collegiate Enrollment**: Status must be actively `Active`

### Classification Hierarchy & Rules

```
                             [ Student Profile ]
                                      │
                     Is Data Valid? (Validation Gate)
                                ├── NO ──> [ Invalid Record ] (Disqualified)
                                │
                               YES
                                │
               Do All 5 Mandatory Conditions Pass?
                                ├── NO ──> [ Not Eligible ]
                                │
                               YES
                                │
               Is CGPA >= 8.50 AND Attendance >= 85%?
                     ├── YES ────────> [ Tier 1: Highly Eligible ]
                     │
                    NO
                     │
              Is CGPA >= 7.00?
                     ├── YES ────────> [ Tier 2: Eligible ]
                     │
              Is 6.75 <= CGPA < 7.00? (Audited Exception)
                     └── YES ────────> [ Tier 3: Conditionally Eligible ]
```

- **Tier 1: Highly Eligible (7 Scholars)**: Achieves academic distinction (`Demo_CGPA >= 8.50`) **and** superior attendance (`Attendance >= 85.0%`) alongside all mandatory criteria.
- **Tier 2: Eligible (934 Scholars)**: Satisfies all 5 standard mandatory conditions.
- **Tier 3: Conditionally Eligible (727 Scholars)**: Qualifies under the audited academic exception (`6.75 <= Demo_CGPA < 7.00`) provided all other 4 mandatory conditions are fully satisfied.
- **Category 4: Not Eligible (4,938 Applicants)**: Fails one or more critical mandatory conditions.
- **Disqualified: Invalid Record (1 Applicant)**: Disqualified at the Phase 2 validation gate (`STU1526` due to `Exam_Score = 101`).

---

## 5. Composite Eligibility Scoring Engine (Out of 100 Points)

In Phase 5, the system computes a multi-dimensional composite score for institutional advising:

| Component | Weight | Mathematical Formula / Policy |
|---|---|---|
| **Academic Merit** | **40 Points** | $\text{Academic Score} = \left(\frac{\text{Demo\_CGPA}}{10.0}\right) \times 40.0$ |
| **Attendance Consistency** | **30 Points** | $\text{Attendance Score} = \left(\frac{\text{Attendance}}{100.0}\right) \times 30.0$ |
| **Financial Need Index** | **20 Points** | Low Income ($\le \text{₹2,00,000}$) = 20 pts<br>Medium Income ($\le \text{₹5,00,000}$) = 10 pts<br>High Income ($> \text{₹5,00,000}$) = 0 pts |
| **Merit & Discipline Boost** | **10 Points** | Extracurricular Participation (`Yes`) = 5 pts<br>Zero Active Backlogs (`0`) = 5 pts |
| **Total Index** | **100 Points** | $\min(\text{Academic} + \text{Attendance} + \text{Financial} + \text{Boost}, 100.00)$ |

> [!IMPORTANT]
> **Institutional Policy: Rank is by category and tie-breakers; Score is informational.**  
> Official institutional merit rank is **never** determined by the 100-point score. Rank is determined strictly by Category Tier followed by the four-level deterministic tie-breaking hierarchy.

---

## 6. Merit Ranking & Four-Tier Tie-Breaking Protocol

All **1,668 qualified scholars** are ranked using Python's stable `sorted()` algorithm with multi-key lambda expressions:

```python
sorted_students = sorted(
    students_list,
    key=lambda s: (-get_cgpa(s), -get_attendance(s), get_income(s), get_student_id(s))
)
```

### Institutional Priority Hierarchy:
1. **Category Priority**:
   - `Tier 1: Highly Eligible` (Ranks #1 through #7)
   - `Tier 2: Eligible` (Ranks #8 through #941)
   - `Tier 3: Conditionally Eligible` (Ranks #942 through #1,668)
2. **Within-Tier Tie-Breakers**:
   - **Priority 1**: Higher `Demo_CGPA` ranks first (Descending).
   - **Priority 2**: If CGPA is equal, higher `Attendance` ranks first (Descending).
   - **Priority 3**: If CGPA & Attendance are equal, lower `Demo_Family_Income` ranks first (Ascending $\rightarrow$ prioritizes greater financial need).
   - **Priority 4**: If all three match, `Student_ID` in alphabetical order (Ascending $\rightarrow$ deterministic stability).

---

## 7. Dataset Statistics & Verified Baseline Metrics

Every metric is dynamically calculated and cryptographically verified against the 6,607-row Kaggle dataset:

| Metric | Count | Percentage | Description |
|---|---|---|---|
| **Total Applications** | **6,607** | 100.00% | Total records processed |
| **Valid Student Records** | **6,606** | 99.98% | Passed Phase 2 Data Integrity Gate |
| **Invalid Records Disqualified** | **1** | 0.02% | `STU1526` (`Exam_Score = 101`, out of range) |
| **Tier 1: Highly Eligible** | **7** | 0.11% | Distinction Scholars (Ranked #1 to #7) |
| **Tier 2: Eligible** | **934** | 14.14% | Standard Qualified Scholars (Ranked #8 to #941) |
| **Tier 3: Conditionally Eligible** | **727** | 11.00% | Audited Exception Scholars (Ranked #942 to #1,668) |
| **Category 4: Not Eligible** | **4,938** | 74.74% | Failed one or more mandatory conditions |
| **Total Qualified Scholars** | **1,668** | 25.25% | Ranked on Institutional Merit List |
| **Dataset Baseline SHA-256** | `e8df8c4148ef83fb295ca1c092f2c6ee15272c0a8e3018b769a788ab50e96e97` | Verified | Zero file tampering detected |

---

## 8. Interactive Console Application Architecture (`src/main.py`)

The system provides a comprehensive, interactive terminal-based interface designed specifically for college practical examinations:

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

### Key Console Capabilities:
1. **Option 1: Display All Applications**: Browse 6,607 student profiles with clean terminal pagination.
2. **Option 2: Screen Individual Student**: Immediate evaluation by Student ID (e.g., `STU4193`, `STU1526`) displaying all 5 rule checks, 100-point score, and exact decision explanation.
3. **Option 3: Screen All Students**: Batch-evaluates all 6,607 records into in-memory data structures in milliseconds.
4. **Option 4: Search Student**: Case-insensitive substring search by Student ID or Student Name with dynamic result counts.
5. **Option 5: Display Eligible Students**: Lists all 1,668 qualified scholars across Tiers 1, 2, and 3.
6. **Option 6: Display Highly Eligible Students**: Spotlight on the 7 distinction scholars meeting Tier 1 criteria.
7. **Option 7: Rank Eligible Students**: Displays official merit list sorted by 4-tier tie-breaking hierarchy with custom display limits.
8. **Option 8: Display Scholarship Summary**: Displays high-level screening metrics, rejection distributions, and prompts for report generation.
9. **Option 9: Display Screening Date and Time**: Shows current timestamp and system status.
10. **Option 10: Exit**: Safely terminates the session without leaving lingering processes.

---

## 9. Complete Project Directory Structure

```text
Scholarship_Eligibility_System/
│
├── dataset/
│   └── original_dataset.csv             # Kaggle dataset (6,607 rows, SHA-256 verified)
│
├── reports/                             # Generated timestamped institutional reports
│   ├── scholarship_summary_report_*.txt # ASCII summary report with statistics
│   ├── screening_results_*.csv          # 6,607-row institutional screening dataset
│   └── screening_audit_report_*.txt     # SHA-256 cryptographic audit sign-off
│
├── src/                                 # Pure Python standard library engine
│   ├── inspect_dataset.py               # Phase 1: CSV Inspection & Golden Hash Baseline
│   ├── data_loader.py                   # Phase 2: CSV Parsing & Proxy Field Preparation
│   ├── validation.py                    # Phase 2: 10-Rule Data Integrity Gate
│   ├── eligibility.py                   # Phases 3-5: Threshold Rules, Classification & Scoring
│   ├── ranking.py                       # Phase 6: Merit Ranking & 4-Tier Tie-Breaking
│   ├── report.py                        # Phase 7: Reporting & Audit File Generation
│   └── main.py                          # Phase 8: Master Interactive Menu-Driven CLI
│
├── Project_Report_BWU.md                # Full academic project report (BWU format)
├── Project_Report_BWU.doc               # Word document report (Calibri, printable)
├── README.md                            # Comprehensive Master Documentation & Viva Guide
└── requirements.txt                     # Standard library specification (zero pip packages)
```

---

## 10. Execution & Running Instructions

### Running the Interactive Console Application (Terminal)

1. Open PowerShell or Command Prompt in the project directory:
   ```powershell
   cd c:\Users\suman\OneDrive\Desktop\python\Scholarship_Eligibility_System
   ```
2. Launch the application:
   ```powershell
   python src/main.py
   ```
   *(No pip packages or virtual environment needed — runs instantly on pure Python standard library!)*

---

### Running Individual Module Test Suites

Each module contains standalone verification tests with automated assertions:

```powershell
# Phase 1: Dataset Inspection
python src/inspect_dataset.py

# Phase 2: Data Loader & Validation Gate
python src/data_loader.py
python src/validation.py

# Phases 3-5: Eligibility Checking, Classification & Scoring
python src/eligibility.py

# Phase 6: Merit Ranking & Tie-Breaking
python src/ranking.py

# Phase 7: Report Generation & Cryptographic Audit
python src/report.py
```

---

## 11. Viva Voce & Practical Examination Questions & Answers

### Q1: Why did you choose a rule-based system instead of a Machine Learning (ML) model?
> **Answer:** Machine Learning models are probabilistic "black-box" systems that can suffer from training bias, unpredictable errors, and a lack of explainability. Scholarship allocation involves legal, ethical, and institutional responsibility. A deterministic rule-based system guarantees 100% transparency, repeatability, and accountability—every applicant receives an exact rule-by-rule justification for why they qualified or failed.

### Q2: Why did you avoid Pandas and NumPy in the core engine?
> **Answer:** For a core computer science practical examination, using built-in Python modules (`csv`, `os`, `sys`, `datetime`, `hashlib`) demonstrates a fundamental mastery of Python data structures (lists, dictionaries, tuples), algorithmic sorting (multi-level lambda keys), defensive input handling, and standard file I/O, without relying on third-party abstractions.

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

### Q7: Why did you build the project as a pure terminal/console application with zero external dependencies?
> **Answer:** For a core computer science practical examination, building an interactive terminal application strictly using Python's standard library (`csv`, `os`, `sys`, `datetime`, `hashlib`) proves deep mastery of fundamental computer science concepts: algorithmic complexity, data structures (dictionaries, tuples, lists), defensive stream I/O, error handling, and clean code architecture. It requires zero package installations, eliminates environmental discrepancies during practical exams, and executes at lightning speed on any standard Python setup.

### Q8: What is the difference between the 100-point composite score and the institutional merit rank?
> **Answer:** The 100-point score is purely **informational**—it aggregates academic performance (40 pts), attendance (30 pts), financial need (20 pts), and discipline boost (10 pts) for student advising. The **official merit rank** is determined strictly by Category Tier (Tier 1 Highly Eligible first $\rightarrow$ Tier 2 Eligible second $\rightarrow$ Tier 3 Conditionally Eligible third) followed by the 4-tier tie-breaking hierarchy (`CGPA` desc $\rightarrow$ `Attendance` desc $\rightarrow$ `Family Income` asc $\rightarrow$ `Student_ID` asc). A student with a high score in Tier 2 will never outrank a Tier 1 Highly Eligible scholar.

### Q9: Who are the key showcase students for practical demonstration?
> **Answer:**
> - **`STU4193`**: **Rank #1** overall institutional scholar (Highly Eligible, CGPA 9.80, Attendance 90.0%, Income ₹2,00,000).
> - **`STU2426`**: **Rank #8** overall scholar (Top of Tier 2 Eligible, CGPA 9.90, Attendance 83.0%, Income ₹4,50,000).
> - **`STU0001`**: Classified as **Eligible** (CGPA 6.70 standard/conditional pass, Attendance 84.0%).
> - **`STU1526`**: Classified as **Invalid Record** (Disqualified by data integrity gate due to `Exam_Score = 101`).
