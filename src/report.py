"""
Scholarship Eligibility Screening System
Module: report.py
Phase: 7 - Consolidated Reporting and Audit File Generation Module

Description:
    This module implements Phase 7 of the BCA college project:
    "Scholarship Eligibility Screening System Using Rule-Based Conditions".
    
    It generates institutional audit documents, CSV screening datasets, and
    text summary reports based on student evaluations from Phases 3-5.
    
Required Functions:
    1. generate_summary(evaluated_students)
    2. generate_student_report(student)
    3. export_results_to_csv(evaluated_students, filename)
    4. generate_text_report(evaluated_students, filename)
    5. generate_audit_report(evaluated_students, filename)
    6. generate_all_reports(evaluated_students)
    7. run_phase_7_tests()

Key Architectural Principles:
    - AUDITABILITY & TIMESTAMPING: Every report is stamped with live datetime.now().
    - IMMUTABILITY: The original Kaggle CSV is never modified or overwritten.
    - CRYPTOGRAPHIC VERIFICATION: SHA-256 checksum checks verify dataset integrity.
    - DEMO TRANSPARENCY: Clearly labels synthetic/proxy fields (Demo_CGPA,
      Demo_Family_Income, Demo_Backlogs, Demo_Enrollment_Status) as demonstration data.
    - CORE PYTHON ONLY: Uses built-in modules only (csv, os, datetime, hashlib, sys).
      No Pandas, NumPy, or third-party libraries.

Author: BCA Student Developer
Advisor: Senior Python Developer & Mentor
"""

import os
import sys
import csv
import hashlib
from datetime import datetime

# Path resolution for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from data_loader import load_students
    from eligibility import calculate_eligibility, evaluate_all_students
except ImportError:
    from src.data_loader import load_students
    from src.eligibility import calculate_eligibility, evaluate_all_students


# =============================================================================
# HELPER & INTEGRITY FUNCTIONS
# =============================================================================

def get_reports_directory():
    """
    Safely locates and creates the 'reports/' directory in the project workspace.
    
    Returns:
        str: Absolute path to the reports directory.
    """
    reports_dir = os.path.join(os.getcwd(), "reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir, exist_ok=True)
    return reports_dir


def check_csv_integrity(filepath="dataset/original_dataset.csv", expected_hash="e8df8c4148ef83fb295ca1c092f2c6ee15272c0a8e3018b769a788ab50e96e97"):
    """
    Computes and verifies the SHA-256 cryptographic checksum of the original dataset.
    This guarantees that the raw Kaggle dataset has never been modified or overwritten.
    
    Parameters:
        filepath (str): Path to original_dataset.csv.
        expected_hash (str): Known golden baseline SHA-256 hash.
        
    Returns:
        tuple: (is_intact: bool, current_hash: str)
    """
    if not os.path.exists(filepath):
        return False, "FILE_NOT_FOUND"

    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    current_hash = sha256.hexdigest()
    return (current_hash == expected_hash), current_hash


def ensure_evaluated(student):
    """
    Defensively ensures that a student record has been evaluated by Phases 3-5.
    If already evaluated, returns it directly; otherwise, runs calculate_eligibility().
    
    Parameters:
        student (dict): Raw student dict or evaluated student dict.
        
    Returns:
        dict: Evaluated student dictionary.
    """
    if isinstance(student, dict) and "classification" in student and "is_valid_data" in student:
        return student
    return calculate_eligibility(student)


def get_student_id_val(student_eval):
    """Safely extracts Student_ID from an evaluated record."""
    return student_eval.get("student_id", student_eval.get("Student_ID", "UNKNOWN"))


def get_student_name_val(student_eval):
    """Safely extracts Student_Name from an evaluated record."""
    return student_eval.get("student_name", student_eval.get("Student_Name", "UNKNOWN"))


# =============================================================================
# REQUIREMENT A: generate_summary(evaluated_students)
# =============================================================================

def generate_summary(evaluated_students):
    """
    Calculates consolidated statistical metrics across evaluated student records.
    
    Computes:
    - Total student applications
    - Valid records
    - Invalid records
    - Highly Eligible students
    - Eligible students
    - Conditionally Eligible students
    - Not Eligible students
    - Total eligible students
    
    Enforces total count consistency:
      valid_records + invalid_records == total_applications
      highly_eligible + eligible + conditionally_eligible + not_eligible + invalid_records == total_applications
      total_eligible == highly_eligible + eligible + conditionally_eligible
      
    Parameters:
        evaluated_students (list): List of student evaluation dictionaries.
        
    Returns:
        dict: Summary statistics dictionary.
    """
    total = len(evaluated_students)
    valid_count = 0
    invalid_count = 0
    highly_eligible = 0
    eligible = 0
    conditionally_eligible = 0
    not_eligible = 0

    for s in evaluated_students:
        eval_record = ensure_evaluated(s)
        is_valid = eval_record.get("is_valid_data", True)
        classification = eval_record.get("classification", "")

        if not is_valid or classification == "Invalid Record":
            invalid_count += 1
        else:
            valid_count += 1
            if classification == "Highly Eligible":
                highly_eligible += 1
            elif classification == "Eligible":
                eligible += 1
            elif classification == "Conditionally Eligible":
                conditionally_eligible += 1
            elif classification == "Not Eligible":
                not_eligible += 1

    total_eligible = highly_eligible + eligible + conditionally_eligible

    return {
        "total_applications": total,
        "valid_records": valid_count,
        "invalid_records": invalid_count,
        "highly_eligible": highly_eligible,
        "eligible": eligible,
        "conditionally_eligible": conditionally_eligible,
        "not_eligible": not_eligible,
        "total_eligible": total_eligible,
    }


# =============================================================================
# REQUIREMENT B: generate_student_report(student)
# =============================================================================

def generate_student_report(student):
    """
    Generates a readable report for an individual student profile.
    
    Contains:
    - Student ID
    - Student name
    - CGPA (Demo_CGPA proxy)
    - Attendance percentage
    - Family income (Demo_Family_Income proxy)
    - Backlogs count (Demo_Backlogs proxy)
    - Enrollment status (Demo_Enrollment_Status proxy)
    - Validation status
    - Eligibility classification
    - Individual eligibility conditions
    - Decision explanation
    
    Clearly labels synthetic demonstration fields as demo data.
    
    Parameters:
        student (dict): Student record (raw or evaluated).
        
    Returns:
        str: Formatted human-readable student profile report.
    """
    eval_record = ensure_evaluated(student)
    is_valid = eval_record.get("is_valid_data", True)
    sid = get_student_id_val(eval_record)
    sname = get_student_name_val(eval_record)
    classification = eval_record.get("classification", "Unknown")
    is_eligible = eval_record.get("is_eligible", False)
    explanation = eval_record.get("explanation", "")

    lines = []
    lines.append("=" * 80)
    lines.append("        STUDENT SCHOLARSHIP ELIGIBILITY SCREENING REPORT        ")
    lines.append("=" * 80)
    lines.append(f"Student ID                 : {sid}")
    lines.append(f"Student Name               : {sname}")
    lines.append(f"Validation Status          : {'Valid Record' if is_valid else 'Invalid Record'}")
    lines.append(f"Eligibility Classification : {classification}")
    score_info = eval_record.get("eligibility_score", {})
    total_score = score_info.get("total_score", 0.0) if isinstance(score_info, dict) else float(score_info or 0.0)
    lines.append(f"Eligibility Score (100 Max): {total_score:.2f} / 100.00")
    lines.append(f"Overall Decision           : {'Eligible' if is_eligible else 'Not Eligible'}")
    lines.append("-" * 80)
    lines.append("INDIVIDUAL ELIGIBILITY CONDITIONS EVALUATION:")

    if is_valid:
        checks = eval_record.get("checks", {})
        acad = checks.get("academic", {})
        att = checks.get("attendance", {})
        inc = checks.get("income", {})
        back = checks.get("backlogs", {})
        enr = checks.get("enrollment", {})

        acad_status = "PASS" if acad.get("passed_standard") else ("CONDITIONAL (Exception)" if acad.get("passed_conditional") else "FAIL")
        att_status = "PASS" if att.get("passed") else "FAIL"
        inc_status = "PASS" if inc.get("passed") else "FAIL"
        back_status = "PASS" if back.get("passed") else "FAIL"
        enr_status = "PASS" if enr.get("passed") else "FAIL"

        lines.append(f"  1. Academic CGPA [Demo Data]       : {acad.get('cgpa', 0.0):.2f} (Required: >= 7.00, Exception: >= 6.75) -> [{acad_status}]")
        lines.append(f"  2. Attendance Rate                 : {att.get('attendance', 0.0):.1f}% (Required: >= 75.0%) -> [{att_status}]")
        lines.append(f"  3. Family Income (INR) [Demo Data] : ₹{inc.get('income', 0):,} (Required: <= ₹500,000) -> [{inc_status}]")
        lines.append(f"  4. Active Backlogs [Demo Data]     : {back.get('backlogs', 0)} (Required: <= 1) -> [{back_status}]")
        lines.append(f"  5. Enrollment Status [Demo Data]   : {enr.get('status', 'Unknown')} (Required: Active) -> [{enr_status}]")
    else:
        lines.append("  Data integrity validation failed prior to rule-based evaluation.")
        errors = eval_record.get("validation_errors", [])
        for err in errors:
            lines.append(f"  - Validation Error: {err}")

    lines.append("-" * 80)
    lines.append("DECISION EXPLANATION:")
    lines.append(explanation)
    lines.append("=" * 80)
    return "\n".join(lines)


# =============================================================================
# REQUIREMENT C: export_results_to_csv(evaluated_students, filename)
# =============================================================================

def export_results_to_csv(evaluated_students, filename):
    """
    Exports student screening results into a structured CSV file using Python's
    built-in csv module (csv.DictWriter).
    
    Columns:
    - Student_ID
    - Student_Name
    - Demo_CGPA
    - Attendance
    - Demo_Family_Income
    - Demo_Backlogs
    - Demo_Enrollment_Status
    - Validation_Status
    - Eligibility_Classification
    - Is_Eligible
    - Decision_Explanation
    
    Parameters:
        evaluated_students (list): List of evaluated student dictionaries.
        filename (str): Destination file path for CSV export.
        
    Returns:
        str: Path to the generated CSV file.
    """
    fieldnames = [
        "Student_ID",
        "Student_Name",
        "Demo_CGPA",
        "Attendance",
        "Demo_Family_Income",
        "Demo_Backlogs",
        "Demo_Enrollment_Status",
        "Validation_Status",
        "Eligibility_Classification",
        "Is_Eligible",
        "Decision_Explanation"
    ]

    # Ensure parent directory exists
    parent_dir = os.path.dirname(os.path.abspath(filename))
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    with open(filename, mode="w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for s in evaluated_students:
            eval_record = ensure_evaluated(s)
            is_valid = eval_record.get("is_valid_data", True)
            checks = eval_record.get("checks", {})

            if is_valid:
                acad = checks.get("academic", {})
                att = checks.get("attendance", {})
                inc = checks.get("income", {})
                back = checks.get("backlogs", {})
                enr = checks.get("enrollment", {})

                cgpa_val = f"{acad.get('cgpa'):.2f}" if acad.get("cgpa") is not None else "N/A"
                att_val = f"{att.get('attendance'):.1f}" if att.get("attendance") is not None else "N/A"
                inc_val = inc.get("income", "N/A")
                back_val = back.get("backlogs", "N/A")
                enr_val = enr.get("status", "N/A")
                val_status = "Valid"
            else:
                cgpa_val = "N/A"
                att_val = "N/A"
                inc_val = "N/A"
                back_val = "N/A"
                enr_val = "N/A"
                val_status = "Invalid"

            row = {
                "Student_ID": get_student_id_val(eval_record),
                "Student_Name": get_student_name_val(eval_record),
                "Demo_CGPA": cgpa_val,
                "Attendance": att_val,
                "Demo_Family_Income": inc_val,
                "Demo_Backlogs": back_val,
                "Demo_Enrollment_Status": enr_val,
                "Validation_Status": val_status,
                "Eligibility_Classification": eval_record.get("classification", "Unknown"),
                "Is_Eligible": eval_record.get("is_eligible", False),
                "Decision_Explanation": eval_record.get("explanation", "")
            }
            writer.writerow(row)

    return filename


# =============================================================================
# REQUIREMENT D: generate_text_report(evaluated_students, filename)
# =============================================================================

def generate_text_report(evaluated_students, filename):
    """
    Generates a professional, comprehensive ASCII .txt summary report.
    
    Includes:
    1. Project title
    2. Report generation date and time using datetime
    3. Dataset information
    4. Total applications
    5. Validation summary
    6. Eligibility summary
    7. Category-wise student counts
    8. Overall eligible percentage
    9. Decision rules summary
    10. Important notes about demonstration data
    
    Parameters:
        evaluated_students (list): List of evaluated student dictionaries.
        filename (str): Destination file path for the text report.
        
    Returns:
        str: File path of the written report.
    """
    summary = generate_summary(evaluated_students)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total = summary["total_applications"]
    valid = summary["valid_records"]
    invalid = summary["invalid_records"]
    highly = summary["highly_eligible"]
    eligible = summary["eligible"]
    cond = summary["conditionally_eligible"]
    not_el = summary["not_eligible"]
    tot_el = summary["total_eligible"]

    valid_pct = (valid / total * 100) if total > 0 else 0.0
    invalid_pct = (invalid / total * 100) if total > 0 else 0.0
    eligible_pct = (tot_el / total * 100) if total > 0 else 0.0
    not_el_pct = (not_el / total * 100) if total > 0 else 0.0

    # Cryptographically check dataset integrity
    csv_intact, current_hash = check_csv_integrity()

    lines = []
    lines.append("=" * 80)
    lines.append("        SCHOLARSHIP ELIGIBILITY SCREENING SYSTEM        ")
    lines.append("          INSTITUTIONAL SCREENING SUMMARY REPORT        ")
    lines.append("=" * 80)
    lines.append(f"Report Generated On : {timestamp}")
    lines.append("Project Title       : Scholarship Eligibility Screening System Using Rule-Based Conditions")
    lines.append("System Architecture : Core Deterministic Rule Engine (Core Python Only)")
    lines.append("Academic Scope      : BCA College Project Demonstration")
    lines.append("-" * 80)
    lines.append("")
    lines.append("1. DATASET INFORMATION")
    lines.append("-" * 80)
    lines.append("Dataset Source Path : dataset/original_dataset.csv")
    lines.append(f"Total Student Rows  : {total:,}")
    lines.append("Underlying Dataset  : Kaggle Student Performance Dataset (Secondary Education)")
    if csv_intact:
        lines.append("Dataset Integrity   : SHA-256 matches recorded baseline")
    else:
        lines.append("Dataset Integrity   : WARNING - Verification failed")
    lines.append("")
    lines.append("2. DATA VALIDATION SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Applications Processed : {total:,}")
    lines.append(f"Valid Student Records        : {valid:,} ({valid_pct:.2f}%)")
    lines.append(f"Invalid Data Records         : {invalid:,} ({invalid_pct:.2f}%)")
    if invalid > 0:
        lines.append("  * Note: Invalid records failed data type or boundary checks (e.g. Exam_Score > 100)")
        lines.append("    and were safely disqualified prior to rule-based evaluation.")
    lines.append("")
    lines.append("3. ELIGIBILITY DECISION SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Eligible Candidates    : {tot_el:,} ({eligible_pct:.2f}%)")
    lines.append(f"Total Ineligible Candidates  : {not_el:,} ({not_el_pct:.2f}%)")
    lines.append(f"Overall Eligibility Rate     : {eligible_pct:.2f}%")
    lines.append("")
    lines.append("4. CATEGORY-WISE STUDENT CLASSIFICATION")
    lines.append("-" * 80)
    h_pct = (highly / total * 100) if total > 0 else 0.0
    e_pct = (eligible / total * 100) if total > 0 else 0.0
    c_pct = (cond / total * 100) if total > 0 else 0.0
    lines.append(f"  • Category 1: Highly Eligible        : {highly:>5,} candidates ({h_pct:6.2f}%)")
    lines.append(f"  • Category 2: Eligible               : {eligible:>5,} candidates ({e_pct:6.2f}%)")
    lines.append(f"  • Category 3: Conditionally Eligible : {cond:>5,} candidates ({c_pct:6.2f}%)")
    lines.append(f"  • Category 4: Not Eligible           : {not_el:>5,} candidates ({not_el_pct:6.2f}%)")
    lines.append(f"  • Disqualified (Invalid Record)      : {invalid:>5,} candidates ({invalid_pct:6.2f}%)")
    lines.append(f"  Total Verified Records              : {total:>5,} records")
    lines.append("")
    lines.append("5. DECISION RULES SUMMARY")
    lines.append("-" * 80)
    lines.append("A candidate must satisfy all 5 mandatory conditions to qualify for a scholarship:")
    lines.append("  1. Academic CGPA     : Minimum 7.00 on 10.00 scale (Demo_CGPA)")
    lines.append("  2. Attendance Rate   : Minimum 75.0% attendance")
    lines.append("  3. Family Income     : Annual family income <= ₹500,000 (Demo_Family_Income)")
    lines.append("  4. Active Backlogs   : Maximum 1 backlog allowed (Demo_Backlogs)")
    lines.append("  5. Enrollment Status : Must be currently 'Active' (Demo_Enrollment_Status)")
    lines.append("")
    lines.append("Classification Tiers:")
    lines.append("  - Highly Eligible       : All mandatory pass AND Demo_CGPA >= 8.50 AND Attendance >= 85%")
    lines.append("  - Eligible              : All 5 mandatory conditions pass under standard thresholds")
    lines.append("  - Conditionally Eligible : Demo_CGPA 6.75 - 6.99 (Academic Exception) AND all other 4 pass")
    lines.append("  - Not Eligible          : Fails one or more critical mandatory conditions")
    lines.append("")
    lines.append("6. IMPORTANT NOTES ON DEMONSTRATION DATA")
    lines.append("-" * 80)
    lines.append("The original Kaggle Student Performance Dataset does NOT contain authentic Indian CGPA,")
    lines.append("annual family income in Rupees, active backlogs, or college enrollment statuses.")
    lines.append("To simulate institutional scholarship screening for this BCA college project,")
    lines.append("the following fields are clearly labeled as synthetic demonstration (Demo) data:")
    lines.append("  - Demo_CGPA             : Derived demonstration proxy (Exam_Score / 10.0)")
    lines.append("  - Demo_Family_Income    : Mapped demonstration INR proxy from Kaggle categories")
    lines.append("  - Demo_Backlogs         : Simulated active backlogs (0 to 2)")
    lines.append("  - Demo_Enrollment_Status: Simulated college enrollment status ('Active' / 'Inactive')")
    lines.append("These proxy fields are used solely for academic demonstration and do not reflect")
    lines.append("real-world financial or academic scholarship determinations.")
    lines.append("=" * 80)

    # Ensure parent directory exists
    parent_dir = os.path.dirname(os.path.abspath(filename))
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    with open(filename, mode="w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filename


# =============================================================================
# REQUIREMENT E: generate_audit_report(evaluated_students, filename)
# =============================================================================

def generate_audit_report(evaluated_students, filename, generated_files=None):
    """
    Generates a formal audit and compliance report.
    
    Contains:
    - Project title
    - Exact report-generation timestamp using datetime
    - Total records processed
    - Valid records
    - Invalid records
    - Eligibility decisions
    - Number of records in each classification
    - Report filenames generated
    - Confirmation that the original CSV was not intentionally modified
      (verified cryptographically via SHA-256 before making any claim).
      
    Parameters:
        evaluated_students (list): List of evaluated student dictionaries.
        filename (str): Destination path for audit report text file.
        generated_files (dict, optional): Mapping of report labels to file paths.
        
    Returns:
        str: Path to the generated audit report.
    """
    summary = generate_summary(evaluated_students)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Cryptographically verify the original CSV integrity
    csv_intact, current_hash = check_csv_integrity()

    lines = []
    lines.append("=" * 80)
    lines.append("            SCHOLARSHIP ELIGIBILITY SCREENING SYSTEM            ")
    lines.append("                 SYSTEM AUDIT & COMPLIANCE LOG                  ")
    lines.append("=" * 80)
    lines.append(f"Audit Execution Timestamp : {timestamp}")
    lines.append("Project Title             : Scholarship Eligibility Screening System Using Rule-Based Conditions")
    lines.append("Audit Scope               : Full Pipeline Execution, Data Integrity & Output Verification")
    lines.append("-" * 80)
    lines.append("")
    lines.append("1. PROCESSING & EVALUATION METRICS")
    lines.append("-" * 80)
    lines.append(f"Total Records Processed       : {summary['total_applications']:,}")
    lines.append(f"Valid Records Verified        : {summary['valid_records']:,}")
    lines.append(f"Invalid Records Disqualified  : {summary['invalid_records']:,}")
    lines.append(f"Total Eligible Candidates     : {summary['total_eligible']:,}")
    lines.append(f"Total Ineligible Candidates   : {summary['not_eligible']:,}")
    lines.append("")
    lines.append("2. CLASSIFICATION BREAKDOWN")
    lines.append("-" * 80)
    lines.append(f"  • Highly Eligible           : {summary['highly_eligible']:,}")
    lines.append(f"  • Eligible                  : {summary['eligible']:,}")
    lines.append(f"  • Conditionally Eligible    : {summary['conditionally_eligible']:,}")
    lines.append(f"  • Not Eligible              : {summary['not_eligible']:,}")
    lines.append(f"  • Invalid Record            : {summary['invalid_records']:,}")
    lines.append("")
    lines.append("3. GENERATED REPORT ARTIFACTS")
    lines.append("-" * 80)
    if generated_files:
        for key, path in generated_files.items():
            lines.append(f"  - {key:<24} : {path}")
    else:
        lines.append(f"  - Audit Report Destination : {filename}")
    lines.append("")
    lines.append("4. ORIGINAL DATASET INTEGRITY VERIFICATION")
    lines.append("-" * 80)
    lines.append("Dataset File Checked : dataset/original_dataset.csv")
    lines.append(f"Computed SHA-256 Hash: {current_hash}")
    if csv_intact:
        lines.append("Integrity Status     : VERIFIED INTACT")
        lines.append("Audit Confirmation   : Current dataset SHA-256 matches the recorded baseline.")
    else:
        lines.append("Integrity Status     : CHECKSUM MISMATCH OR FILE NOT FOUND")
        lines.append("Audit Confirmation   : WARNING - Current dataset SHA-256 does not match recorded baseline.")
    lines.append("=" * 80)

    # Ensure parent directory exists
    parent_dir = os.path.dirname(os.path.abspath(filename))
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    with open(filename, mode="w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filename


# =============================================================================
# REQUIREMENT F: generate_all_reports(evaluated_students)
# =============================================================================

def generate_all_reports(evaluated_students):
    """
    Orchestrates the generation of all Phase 7 reports:
    1. Creates reports/ directory if it does not exist.
    2. Generates the timestamped text summary report.
    3. Generates the timestamped CSV screening report.
    4. Generates the timestamped audit report.
    5. Displays the generated file locations.
    6. Returns a useful summary dictionary of generated files and metrics.
    
    Uses timestamped filenames to prevent accidental overwriting of earlier reports.
    
    Parameters:
        evaluated_students (list): List of evaluated student records.
        
    Returns:
        dict: Summary of generated reports and file paths.
    """
    reports_dir = get_reports_directory()
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Define timestamped filenames
    txt_filename = os.path.join(reports_dir, f"scholarship_summary_report_{timestamp_str}.txt")
    csv_filename = os.path.join(reports_dir, f"screening_results_{timestamp_str}.csv")
    audit_filename = os.path.join(reports_dir, f"screening_audit_report_{timestamp_str}.txt")

    # 1. Generate text summary report
    generate_text_report(evaluated_students, txt_filename)

    # 2. Generate CSV screening report
    export_results_to_csv(evaluated_students, csv_filename)

    # Register generated file paths
    generated_files = {
        "Text Summary Report": txt_filename,
        "Screening Results CSV": csv_filename,
        "Audit Log Report": audit_filename
    }

    # 3. Generate audit report
    generate_audit_report(evaluated_students, audit_filename, generated_files=generated_files)

    # 4. Calculate summary metrics
    summary = generate_summary(evaluated_students)

    result = {
        "summary": summary,
        "text_report": txt_filename,
        "csv_report": csv_filename,
        "audit_report": audit_filename,
        "generated_files": generated_files,
        "timestamp": timestamp_str
    }

    # 5. Display generated file locations
    display_generated_reports_summary(result)

    return result


def display_generated_reports_summary(report_results):
    """
    Prints a clear, structured confirmation of the generated reports to the terminal.
    """
    summary = report_results["summary"]
    print("\n" + "=" * 80)
    print("        SCHOLARSHIP ELIGIBILITY SCREENING SYSTEM        ")
    print("             CONSOLIDATED REPORT GENERATION (PHASE 7)             ")
    print("=" * 80)
    print(f"Timestamp of Generation : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Records Evaluated : {summary['total_applications']:,}")
    print(f"Valid Student Records   : {summary['valid_records']:,}")
    print(f"Invalid Data Records    : {summary['invalid_records']:,}")
    print(f"Total Eligible Scholars : {summary['total_eligible']:,}")
    print(f"Total Ineligible        : {summary['not_eligible']:,}")
    print("-" * 80)
    print("Generated Report Files:")
    for label, path in report_results.get("generated_files", {}).items():
        rel_path = os.path.relpath(path)
        file_size = os.path.getsize(path) if os.path.exists(path) else 0
        print(f"  [+] {label:<22} : {rel_path} ({file_size:,} bytes)")
    print("=" * 80)


# =============================================================================
# REQUIREMENT 5: run_phase_7_tests()
# =============================================================================

def run_phase_7_tests():
    """
    Executes comprehensive unit and integration verification for Phase 7.
    
    Verifies:
    1. Summary counts are correct.
    2. Total category counts match total evaluated records.
    3. Valid and invalid record counts are correct.
    4. Individual student report contains correct information.
    5. CSV file is generated successfully.
    6. CSV headers are correct.
    7. CSV rows match the number of evaluated students.
    8. Text report is generated successfully.
    9. Audit report is generated successfully.
    10. Empty input is handled without errors.
    11. Reports directory is created automatically.
    12. Original CSV integrity remains unchanged (SHA-256 before & after).
    """
    print("\n" + "=" * 80)
    print("              RUNNING PHASE 7 VERIFICATION TEST SUITE              ")
    print("=" * 80)

    # Checkpoint baseline SHA-256 before tests
    csv_path = "dataset/original_dataset.csv"
    intact_before, hash_before = check_csv_integrity(csv_path)
    assert intact_before, f"Dataset integrity check failed before tests! Hash: {hash_before}"
    print(f"[TEST 12 - PRE-CHECK] Original CSV SHA-256: {hash_before} -> INTACT")

    # Load and evaluate dataset
    raw_students = load_students()
    evaluated = evaluate_all_students(raw_students)
    total_evals = len(evaluated)
    assert total_evals == 6607, f"Expected 6,607 evaluated students, got {total_evals}"

    # TEST 1 & 2 & 3: Summary counts and category totals
    summary = generate_summary(evaluated)
    assert summary["total_applications"] == 6607, f"Expected 6607, got {summary['total_applications']}"
    assert summary["valid_records"] == 6606, f"Expected 6606 valid, got {summary['valid_records']}"
    assert summary["invalid_records"] == 1, f"Expected 1 invalid, got {summary['invalid_records']}"
    assert summary["highly_eligible"] == 7, f"Expected 7 highly eligible, got {summary['highly_eligible']}"
    assert summary["eligible"] == 934, f"Expected 934 eligible, got {summary['eligible']}"
    assert summary["conditionally_eligible"] == 727, f"Expected 727 conditional, got {summary['conditionally_eligible']}"
    assert summary["not_eligible"] == 4938, f"Expected 4938 not eligible, got {summary['not_eligible']}"
    assert summary["total_eligible"] == 1668, f"Expected 1668 total eligible, got {summary['total_eligible']}"

    # Category count consistency
    cat_sum = (
        summary["highly_eligible"] +
        summary["eligible"] +
        summary["conditionally_eligible"] +
        summary["not_eligible"] +
        summary["invalid_records"]
    )
    assert cat_sum == summary["total_applications"], f"Category sum ({cat_sum}) != total ({summary['total_applications']})"
    assert summary["valid_records"] + summary["invalid_records"] == summary["total_applications"], "Validation sum mismatch"
    assert summary["total_eligible"] == summary["highly_eligible"] + summary["eligible"] + summary["conditionally_eligible"], "Eligible sum mismatch"
    print("[PASS] Test 1: Summary counts verified against known dataset specifications.")
    print("[PASS] Test 2: Category distribution counts match total evaluated records exactly.")
    print("[PASS] Test 3: Valid (6,606) and invalid (1) record counts verified.")

    # TEST 4: Individual student report verification
    # Test valid candidate
    student_rep = generate_student_report(evaluated[0])
    assert "Student ID" in student_rep, "Student ID missing from student report"
    assert "Student Name" in student_rep, "Student Name missing from student report"
    assert "CGPA [Demo Data]" in student_rep, "Demo_CGPA label missing from student report"
    assert "Attendance Rate" in student_rep, "Attendance missing from student report"
    assert "Family Income (INR) [Demo Data]" in student_rep, "Demo_Family_Income missing from student report"
    assert "Active Backlogs [Demo Data]" in student_rep, "Demo_Backlogs missing from student report"
    assert "Enrollment Status [Demo Data]" in student_rep, "Demo_Enrollment_Status missing from student report"
    assert "Validation Status" in student_rep, "Validation status missing from student report"
    assert "Eligibility Classification" in student_rep, "Eligibility classification missing from student report"
    assert "DECISION EXPLANATION:" in student_rep, "Decision explanation missing from student report"
    assert "Demo Data" in student_rep, "Demonstration data disclosure label missing"

    # Test invalid candidate (STU1526, index 1525)
    invalid_rep = generate_student_report(evaluated[1525])
    assert "STU1526" in invalid_rep, "STU1526 ID missing from invalid student report"
    assert "Invalid Record" in invalid_rep, "Invalid Record classification missing from report"
    assert "Validation Error" in invalid_rep, "Validation error notice missing from report"
    print("[PASS] Test 4: Individual student report contains all required fields and demo disclosures.")

    # TEST 5, 6, 7: CSV export verification
    test_csv = os.path.join(get_reports_directory(), "test_screening_export.csv")
    export_results_to_csv(evaluated, test_csv)
    assert os.path.exists(test_csv), "Test CSV file was not created"
    assert os.path.getsize(test_csv) > 0, "Test CSV file is empty"

    with open(test_csv, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        expected_header = [
            "Student_ID",
            "Student_Name",
            "Demo_CGPA",
            "Attendance",
            "Demo_Family_Income",
            "Demo_Backlogs",
            "Demo_Enrollment_Status",
            "Validation_Status",
            "Eligibility_Classification",
            "Is_Eligible",
            "Decision_Explanation"
        ]
        assert header == expected_header, f"CSV header mismatch: got {header}"

        rows = list(reader)
        assert len(rows) == 6607, f"Expected 6607 CSV rows, got {len(rows)}"

    print("[PASS] Test 5: CSV screening results export generated successfully.")
    print("[PASS] Test 6: CSV headers match exact required schema.")
    print("[PASS] Test 7: CSV row count (6,607) matches total evaluated students exactly.")

    # TEST 8: Text report verification
    test_txt = os.path.join(get_reports_directory(), "test_summary_report.txt")
    generate_text_report(evaluated, test_txt)
    assert os.path.exists(test_txt), "Test text report was not created"
    assert os.path.getsize(test_txt) > 0, "Test text report is empty"

    with open(test_txt, mode="r", encoding="utf-8") as f:
        txt_content = f.read()
        assert "SCHOLARSHIP ELIGIBILITY SCREENING SYSTEM" in txt_content
        assert "Report Generated On" in txt_content
        assert "DATASET INFORMATION" in txt_content
        assert "SHA-256 matches recorded baseline" in txt_content
        assert "DECISION RULES SUMMARY" in txt_content
        assert "IMPORTANT NOTES ON DEMONSTRATION DATA" in txt_content
        assert "6,607" in txt_content

    print("[PASS] Test 8: Comprehensive text summary report generated with all required sections.")

    # TEST 9: Audit report verification
    test_audit = os.path.join(get_reports_directory(), "test_audit_report.txt")
    generate_audit_report(evaluated, test_audit)
    assert os.path.exists(test_audit), "Test audit report was not created"
    assert os.path.getsize(test_audit) > 0, "Test audit report is empty"

    with open(test_audit, mode="r", encoding="utf-8") as f:
        audit_content = f.read()
        assert "SYSTEM AUDIT & COMPLIANCE LOG" in audit_content
        assert "Audit Execution Timestamp" in audit_content
        assert "Current dataset SHA-256 matches the recorded baseline." in audit_content
        assert hash_before in audit_content

    print("[PASS] Test 9: Institutional audit report generated with verified SHA-256 confirmation.")

    # TEST 10: Empty input handling without crash
    empty_summary = generate_summary([])
    assert empty_summary["total_applications"] == 0
    assert empty_summary["valid_records"] == 0
    assert empty_summary["invalid_records"] == 0
    assert empty_summary["total_eligible"] == 0

    empty_csv = os.path.join(get_reports_directory(), "test_empty.csv")
    export_results_to_csv([], empty_csv)
    with open(empty_csv, mode="r", encoding="utf-8") as f:
        empty_rows = list(csv.reader(f))
        assert len(empty_rows) == 1, "Empty CSV should contain only the header row"

    empty_txt = os.path.join(get_reports_directory(), "test_empty.txt")
    generate_text_report([], empty_txt)
    assert os.path.exists(empty_txt)

    empty_audit = os.path.join(get_reports_directory(), "test_empty_audit.txt")
    generate_audit_report([], empty_audit)
    assert os.path.exists(empty_audit)
    print("[PASS] Test 10: Empty input [] handled safely across all reporting functions without error.")

    # TEST 11: Reports directory verification
    assert os.path.exists(get_reports_directory()), "Reports directory does not exist"
    print("[PASS] Test 11: Reports directory 'reports/' created and verified automatically.")

    # Clean up test artifacts
    for temp_file in [test_csv, test_txt, test_audit, empty_csv, empty_txt, empty_audit]:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass

    # TEST 12: Original CSV integrity verification after all tests
    intact_after, hash_after = check_csv_integrity(csv_path)
    assert intact_after, f"Original CSV integrity compromised during test execution! Hash: {hash_after}"
    assert hash_after == hash_before, f"Hash mismatch: before={hash_before}, after={hash_after}"
    print(f"[PASS] Test 12: Original CSV integrity verified UNCHANGED before and after:")
    print(f"        SHA-256 Before : {hash_before}")
    print(f"        SHA-256 After  : {hash_after}")

    print("=" * 80)
    print("             ALL 12 PHASE 7 VERIFICATION TESTS PASSED!             ")
    print("=" * 80)


# Alias for backward compatibility
run_phase_6_tests = run_phase_7_tests


# =============================================================================
# MAIN PIPELINE EXECUTION
# =============================================================================

def run_phase_7_pipeline():
    """
    Executes the complete Phase 7 pipeline:
    1. Loads the Kaggle student dataset.
    2. Evaluates all student records through the Phases 3-5 eligibility rules engine.
    3. Runs Phase 7 test suite with assertions.
    4. Generates all timestamped institutional reports.
    5. Displays terminal summary.
    """
    print("\n" + "=" * 80)
    print(" SCHOLARSHIP ELIGIBILITY SCREENING SYSTEM ")
    print("     PHASE 7: CONSOLIDATED REPORTING & AUDIT GENERATION ")
    print("=" * 80)

    # 1. Load dataset
    print("\n[Step 1/4] Loading student records from Kaggle CSV...")
    raw_students = load_students()
    print(f"           Successfully loaded {len(raw_students):,} student records.")

    # 2. Evaluate students
    print("\n[Step 2/4] Evaluating eligibility using Phases 3-5 deterministic rules engine...")
    evaluations = evaluate_all_students(raw_students)
    print(f"           Successfully evaluated {len(evaluations):,} student profiles.")

    # 3. Run Phase 7 verification tests
    print("\n[Step 3/4] Running Phase 7 automated verification tests with assertions...")
    run_phase_7_tests()

    # 4. Generate all official timestamped reports
    print("\n[Step 4/4] Generating official institutional reports in 'reports/' directory...")
    report_results = generate_all_reports(evaluations)

    return report_results


# Alias for backward compatibility
run_phase_6_pipeline = run_phase_7_pipeline


if __name__ == "__main__":
    run_phase_7_pipeline()
