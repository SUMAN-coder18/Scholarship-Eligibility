"""
Scholarship Eligibility Screening System
Module: data_loader.py
Phase: 2 - Data Loading and Data Preparation

Description:
    This module provides a robust, beginner-friendly data loading and preparation
    pipeline. It reads the raw Kaggle 'Student Performance Factors' CSV dataset,
    validates record integrity, converts numerical fields to native Python types,
    preserves all original Kaggle attributes, and adds explicitly labeled
    demonstration proxy fields (Demo_CGPA, Demo_Family_Income, Demo_Backlogs,
    Demo_Enrollment_Status) required for future rule-based screening testing.

Key Principles:
    1. READ-ONLY: Never modifies or overwrites 'dataset/original_dataset.csv'.
    2. TRANSPARENCY: Clearly separates original Kaggle fields from synthetic
       demonstration test fields.
    3. SAFE MISSING VALUE HANDLING: Preserves None / empty markers without
       silently inventing false data.
    4. NO THIRD-PARTY LIBRARIES: Strictly built with standard Python (csv, os).

Author: BCA Student Developer
Advisor: Senior Python Developer & Mentor
"""

import os
import csv


def get_default_dataset_path(filename="original_dataset.csv"):
    """
    Safely resolves the path to the CSV file across different working directories.
    
    Checks:
    1. Relative to Current Working Directory: dataset/<filename>
    2. Relative to Script Directory: ../dataset/<filename>
    
    Parameters:
        filename (str): Name of the dataset file.
        
    Returns:
        str: Valid relative or absolute path.
    """
    path_from_cwd = os.path.join("dataset", filename)
    if os.path.exists(path_from_cwd):
        return path_from_cwd

    script_dir = os.path.dirname(os.path.abspath(__file__))
    path_from_script = os.path.join(script_dir, "..", "dataset", filename)
    if os.path.exists(path_from_script):
        return os.path.normpath(path_from_script)

    return path_from_cwd


def generate_student_id(index):
    """
    Generates a technical, formatted unique student identifier.
    
    Examples:
        index = 1   -> "STU0001"
        index = 25  -> "STU0025"
        index = 6607 -> "STU6607"
        
    Parameters:
        index (int): Sequential 1-based record index.
        
    Returns:
        str: Formatted student identifier string.
    """
    # Using formatted string with zero-padding to 4 digits
    return f"STU{index:04d}"


def validate_csv_record(student_raw):
    """
    Validates the structural integrity and data types of a raw CSV record.
    
    Checks:
    - That mandatory screening columns (Attendance, Exam_Score) are present.
    - That numeric strings can be safely parsed into integers/floats.
    
    Parameters:
        student_raw (dict): Raw dictionary row from csv.DictReader.
        
    Returns:
        tuple: (bool, str) -> (is_valid, validation_message)
    """
    # Check if critical numerical columns exist
    if "Attendance" not in student_raw or "Exam_Score" not in student_raw:
        return False, "Missing mandatory column 'Attendance' or 'Exam_Score'."

    # Validate Attendance conversion
    try:
        att = float(student_raw["Attendance"].strip())
        if att < 0 or att > 100:
            return False, f"Attendance value '{att}' out of range (0-100)."
    except ValueError:
        return False, f"Invalid non-numeric Attendance: '{student_raw.get('Attendance')}'."

    # Validate Exam_Score conversion
    try:
        score = float(student_raw["Exam_Score"].strip())
        if score < 0:
            return False, f"Exam_Score '{score}' cannot be negative."
    except ValueError:
        return False, f"Invalid non-numeric Exam_Score: '{student_raw.get('Exam_Score')}'."

    return True, "Valid"


def prepare_student_data(student_raw, index=1):
    """
    Prepares a clean, typed student dictionary while strictly preserving original
    Kaggle attributes and explicitly segregating synthetic demonstration fields.
    
    Transformations:
    - Numerical conversions: Hours_Studied, Attendance, Sleep_Hours, etc. to int.
    - Missing value handling: Records None where CSV cells are empty.
    - Demo_CGPA: Derived proxy calculated as Exam_Score / 10.0 (capped at 10.00).
    - Demo_Family_Income: Assumed representative rupee value based on categorical bracket.
    - Demo_Backlogs: Explicitly synthetic test count for rule-testing.
    - Demo_Enrollment_Status: Explicitly synthetic status for screening test cases.
    
    Parameters:
        student_raw (dict): Raw dictionary from csv.DictReader.
        index (int): Record index for student ID generation and test variance.
        
    Returns:
        dict: Fully prepared student profile dictionary.
    """
    prepared = {}

    # =========================================================================
    # 1. TECHNICAL IDENTIFIER & NAME (Generated)
    # =========================================================================
    prepared["Student_ID"] = generate_student_id(index)
    prepared["Student_Name"] = f"Student_{index:04d}"

    # =========================================================================
    # 2. ORIGINAL KAGGLE NUMERICAL FIELDS (Converted to Python int/float)
    # =========================================================================
    numerical_keys = [
        "Hours_Studied", "Attendance", "Sleep_Hours", "Previous_Scores",
        "Tutoring_Sessions", "Physical_Activity", "Exam_Score"
    ]

    for key in numerical_keys:
        raw_val = student_raw.get(key, "").strip()
        if raw_val != "":
            try:
                # Converted to int as all these raw Kaggle fields are integer counts/scores
                prepared[key] = int(raw_val)
            except ValueError:
                prepared[key] = float(raw_val)
        else:
            prepared[key] = None  # Safe handling of missing numerical value

    # =========================================================================
    # 3. ORIGINAL KAGGLE CATEGORICAL FIELDS (Preserved with safe None handling)
    # =========================================================================
    categorical_keys = [
        "Parental_Involvement", "Access_to_Resources", "Extracurricular_Activities",
        "Motivation_Level", "Internet_Access", "Family_Income", "Teacher_Quality",
        "School_Type", "Peer_Influence", "Learning_Disabilities",
        "Parental_Education_Level", "Distance_from_Home", "Gender"
    ]

    for key in categorical_keys:
        raw_val = student_raw.get(key, "").strip()
        # Missing values are stored as None rather than invented strings
        prepared[key] = raw_val if raw_val != "" else None

    # =========================================================================
    # 4. EXPLICIT DEMONSTRATION PROXY FIELDS FOR SCHOLARSHIP TESTING
    # (Clearly documented as assumptions for college rule-based demonstration)
    # =========================================================================

    # Demo_CGPA Proxy:
    # Kaggle provides 'Exam_Score' (out of 100, occasionally up to 101).
    # College rule requires CGPA on a 0.00 to 10.00 scale.
    # Conversion formula: Exam_Score / 10.0, safely capped at 10.00.
    exam_score = prepared.get("Exam_Score")
    if exam_score is not None:
        cgpa_calc = round(float(exam_score) / 10.0, 2)
        prepared["Demo_CGPA"] = min(cgpa_calc, 10.00)
    else:
        prepared["Demo_CGPA"] = None

    # Demo_Family_Income Proxy:
    # Kaggle provides categorical 'Low', 'Medium', 'High'.
    # College rule requires annual income <= ₹5,00,000.
    # Representative benchmark assumptions for demonstration testing:
    # - Low    : Assumed representative baseline ₹2,00,000 (Satisfies condition)
    # - Medium : Assumed representative baseline ₹4,50,000 (Satisfies condition)
    # - High   : Assumed representative baseline ₹8,00,000 (Exceeds condition)
    fam_income_cat = prepared.get("Family_Income")
    if fam_income_cat == "Low":
        prepared["Demo_Family_Income"] = 200000
    elif fam_income_cat == "Medium":
        prepared["Demo_Family_Income"] = 450000
    elif fam_income_cat == "High":
        prepared["Demo_Family_Income"] = 800000
    else:
        prepared["Demo_Family_Income"] = None

    # Demo_Backlogs (Synthetic Test Field):
    # Not available in Kaggle dataset.
    # Created purely for testing the conditional rule: 'Backlogs <= 1'.
    # Uses a transparent cyclic test sequence: 0, 0, 1, 0, 2 backlogs.
    # NOT derived from academic performance; purely a test distribution.
    synthetic_backlog_cycle = [0, 0, 1, 0, 2]
    prepared["Demo_Backlogs"] = synthetic_backlog_cycle[(index - 1) % len(synthetic_backlog_cycle)]

    # Demo_Enrollment_Status (Synthetic Test Field):
    # Not available in Kaggle dataset.
    # Created purely for testing the conditional rule: 'Status == Active'.
    # Simulates Active enrollment for ~96% and Inactive for ~4% (every 25th applicant).
    if index % 25 == 0:
        prepared["Demo_Enrollment_Status"] = "Inactive"
    else:
        prepared["Demo_Enrollment_Status"] = "Active"

    return prepared


def load_students(filename=None):
    """
    Loads, validates, and prepares student records from the CSV file.
    
    Parameters:
        filename (str, optional): Custom path to the dataset CSV file.
                                  Defaults to 'dataset/original_dataset.csv'.
                                  
    Returns:
        list: List of prepared student profile dictionaries.
    """
    if filename is None:
        filename = get_default_dataset_path()

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Dataset CSV file not found at: '{filename}'")

    students = []
    skipped_count = 0

    with open(filename, mode="r", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        
        if reader.fieldnames is None:
            raise ValueError(f"CSV file '{filename}' has no header.")

        # Loop through raw records with sequential index
        for index, raw_row in enumerate(reader, start=1):
            is_valid, error_msg = validate_csv_record(raw_row)
            if is_valid:
                prepared_student = prepare_student_data(raw_row, index=index)
                students.append(prepared_student)
            else:
                skipped_count += 1
                print(f"[WARNING] Skipping Row #{index}: {error_msg}")

    return students


def display_student_summary(students):
    """
    Displays a comprehensive summary of the loaded and prepared student dataset.
    
    Includes:
    - Total records loaded.
    - First five prepared records with clear key-value formatting.
    - Generated student ID sample range.
    - Python data types of all attributes.
    - Missing field breakdown across records.
    - Clear distinction between original Kaggle fields and demonstration fields.
    
    Parameters:
        students (list): List of prepared student dictionaries.
    """
    total = len(students)
    print("=" * 65)
    print(" SCHOLARSHIP ELIGIBILITY SCREENING SYSTEM")
    print("       DATA LOADING & PREPARATION MODULE (PHASE 2)")
    print("=" * 65)

    # 1. Total records loaded
    print(f"\n1. TOTAL RECORDS LOADED")
    print("-" * 65)
    print(f"Total Successfully Prepared Records : {total}")
    if total > 0:
        print(f"Generated Student ID Range          : {students[0]['Student_ID']} to {students[-1]['Student_ID']}")

    # 2. First five prepared records
    print("\n" + "-" * 65)
    print("2. FIRST FIVE PREPARED RECORDS")
    print("-" * 65)
    sample_records = students[:5]

    for student in sample_records:
        print(f"\n[Student Identifier: {student['Student_ID']}]")
        print("  • Original Kaggle Academic & Personal Attributes:")
        print(f"      - Attendance                 : {student['Attendance']}%")
        print(f"      - Exam_Score                 : {student['Exam_Score']} (out of 100)")
        print(f"      - Hours_Studied              : {student['Hours_Studied']} hrs/week")
        print(f"      - Previous_Scores            : {student['Previous_Scores']}")
        print(f"      - Extracurricular_Activities : {student['Extracurricular_Activities']}")
        print(f"      - Family_Income (Category)   : {student['Family_Income']}")
        print(f"      - Gender                     : {student['Gender']}")
        print(f"      - Parental_Education_Level   : {student['Parental_Education_Level'] if student['Parental_Education_Level'] else '(MISSING)'}")
        print(f"      - Teacher_Quality            : {student['Teacher_Quality'] if student['Teacher_Quality'] else '(MISSING)'}")
        print(f"      - Distance_from_Home         : {student['Distance_from_Home'] if student['Distance_from_Home'] else '(MISSING)'}")
        print("  • Explicit Demonstration Proxy Fields (For Screening Rules):")
        print(f"      - Demo_CGPA (Proxy)          : {student['Demo_CGPA']:.2f} / 10.00")
        print(f"      - Demo_Family_Income (Proxy) : ₹{student['Demo_Family_Income']:,}")
        print(f"      - Demo_Backlogs (Synthetic)  : {student['Demo_Backlogs']}")
        print(f"      - Demo_Enrollment_Status     : {student['Demo_Enrollment_Status']}")

    # 3. Data types analysis
    print("\n" + "-" * 65)
    print("3. FIELD DATA TYPES IN PREPARED RECORDS")
    print("-" * 65)
    if total > 0:
        sample = students[0]
        for field, value in sample.items():
            type_name = type(value).__name__
            print(f"  {field:<28} : {type_name:<10} (Example: {repr(value)})")

    # 4. Missing value analysis in prepared records
    print("\n" + "-" * 65)
    print("4. MISSING FIELD INFORMATION (Across All Records)")
    print("-" * 65)
    missing_summary = {}
    for student in students:
        for field, val in student.items():
            if val is None:
                missing_summary[field] = missing_summary.get(field, 0) + 1

    if missing_summary:
        for field, count in missing_summary.items():
            pct = (count / total) * 100
            print(f"  {field:<28} : {count} missing records ({pct:.2f}%) -> Handled as None")
    else:
        print("  All fields have complete values.")

    # 5. Original vs Demonstration Fields Comparison Table
    print("\n" + "-" * 65)
    print("5. ORIGINAL KAGGLE FIELDS VS. DEMONSTRATION FIELDS")
    print("-" * 65)
    print(f"  {'Field Name':<26} | {'Classification':<15} | {'Source / Purpose'}")
    print("  " + "-" * 63)
    
    classifications = [
        ("Student_ID", "Generated", "Unique technical identifier (STU0001...)"),
        ("Hours_Studied", "Original", "Kaggle dataset (Integer)"),
        ("Attendance", "Original", "Directly used for screening rule (>= 75%)"),
        ("Exam_Score", "Original", "Kaggle 100-point score (Not CGPA)"),
        ("Extracurricular_Activities", "Original", "Direct binary indicator ('Yes'/'No')"),
        ("Family_Income", "Original", "Categorical ('Low', 'Medium', 'High')"),
        ("Gender", "Original", "Kaggle demographic attribute"),
        ("Parental_Education_Level", "Original", "Contains 90 missing values in Kaggle data"),
        ("Teacher_Quality", "Original", "Contains 78 missing values in Kaggle data"),
        ("Distance_from_Home", "Original", "Contains 67 missing values in Kaggle data"),
        ("Demo_CGPA", "Demonstration", "Derived proxy: Exam_Score / 10.0 (max 10.00)"),
        ("Demo_Family_Income", "Demonstration", "Representative assumed INR (e.g. ₹2L, ₹4.5L, ₹8L)"),
        ("Demo_Backlogs", "Synthetic Test", "Cyclic test values [0,0,1,0,2] for rule testing"),
        ("Demo_Enrollment_Status", "Synthetic Test", "Test status ('Active' ~96%, 'Inactive' ~4%)")
    ]
    
    for fname, fclass, fdesc in classifications:
        print(f"  {fname:<26} | {fclass:<15} | {fdesc}")

    print("\n" + "=" * 65)
    print(" PHASE 2 COMPLETED: DATA LOADING & PREPARATION READY")
    print("=" * 65)


if __name__ == "__main__":
    loaded_students = load_students()
    display_student_summary(loaded_students)
