"""
Scholarship Eligibility Screening System
Module: validation.py
Phase: 2 - Student Data Validation Module (Loading & Validation)

Description:
    This module performs rigorous data integrity and range validation on student
    records before they are processed by the scholarship eligibility engine.
    It verifies that fields such as Student ID, Student Name, CGPA, Exam Score,
    Attendance, Family Income (both Kaggle categorical and Demo numerical),
    Academic Backlogs, Enrollment Status, and Extracurricular participation adhere
    to acceptable data types, physical constraints, and academic scales.

Key Principles:
    1. VALIDITY vs. ELIGIBILITY: Validates whether data is structurally and
       logically correct. It does NOT decide scholarship eligibility (e.g.,
       CGPA 6.50 is VALID data even though it is below the scholarship cutoff).
    2. SEPARATION OF CONCERNS: Validates original Kaggle attributes (Exam_Score,
       Family_Income category) and demonstration proxy fields (Demo_CGPA,
       Demo_Family_Income) separately and transparently.
    3. DEFENSIVE CODING: Safely handles None values, empty strings, and invalid
       data types without program crashes.
    4. NO THIRD-PARTY LIBRARIES: Uses strictly Python core constructs.

Author: BCA Student Developer
Advisor: Senior Python Developer & Mentor
"""

import os
import sys

# Ensure local 'src' directory can be imported cleanly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from data_loader import load_students
except ImportError:
    from src.data_loader import load_students


# =============================================================================
# INDIVIDUAL FIELD VALIDATION FUNCTIONS
# =============================================================================

def validate_student_id(student):
    """
    Validates that the student ID exists and is a non-empty string.
    
    Parameters:
        student (dict): Student dictionary.
        
    Returns:
        tuple: (bool, str) -> (is_valid, message)
    """
    if not isinstance(student, dict):
        return False, "FAIL - Student record must be a dictionary"

    sid = student.get("Student_ID")
    if sid is None:
        return False, "FAIL - Student ID is missing (None)"

    if not isinstance(sid, str):
        return False, f"FAIL - Student ID must be text, got {type(sid).__name__}"

    if sid.strip() == "":
        return False, "FAIL - Student ID cannot be empty or whitespace"

    return True, "PASS"


def validate_student_name(student):
    """
    Validates that the student name exists and is a non-empty string.
    Rejects missing (None) or blank/whitespace student names.
    
    Checks both 'Student_Name' and 'Name' keys for flexibility.
    
    Parameters:
        student (dict): Student dictionary.
        
    Returns:
        tuple: (bool, str) -> (is_valid, message)
    """
    if not isinstance(student, dict):
        return False, "FAIL - Student record must be a dictionary"

    name = student.get("Student_Name")
    if name is None:
        name = student.get("Name")

    if name is None:
        return False, "FAIL - Student name is missing (None)"

    if not isinstance(name, str):
        return False, f"FAIL - Student name must be text, got {type(name).__name__}"

    if name.strip() == "":
        return False, "FAIL - Student name cannot be empty or blank whitespace"

    return True, "PASS"


def validate_cgpa(student):
    """
    Validates that Demo_CGPA is numeric and within the standard Indian university
    scale of 0.00 to 10.00 inclusive.
    
    Parameters:
        student (dict): Student dictionary.
        
    Returns:
        tuple: (bool, str) -> (is_valid, message)
    """
    if not isinstance(student, dict):
        return False, "FAIL - Student record must be a dictionary"

    cgpa = student.get("Demo_CGPA")
    if cgpa is None:
        return False, "FAIL - Demo_CGPA field is missing (None)"

    # Check numeric type (int or float)
    if isinstance(cgpa, bool) or not isinstance(cgpa, (int, float)):
        return False, f"FAIL - CGPA must be numeric, got {type(cgpa).__name__}"

    # Range check: 0.00 to 10.00
    if cgpa < 0.0 or cgpa > 10.0:
        return False, f"FAIL - CGPA must be between 0.0 and 10.0, got {cgpa}"

    return True, "PASS"


def validate_exam_score(student):
    """
    Validates that the original Kaggle Exam_Score is numeric and falls strictly
    between 0 and 100 based on the dataset's documented percentage scale.
    
    Does NOT silently cap scores greater than 100; flags them as invalid.
    
    Parameters:
        student (dict): Student dictionary.
        
    Returns:
        tuple: (bool, str) -> (is_valid, message)
    """
    if not isinstance(student, dict):
        return False, "FAIL - Student record must be a dictionary"

    exam_score = student.get("Exam_Score")
    if exam_score is None:
        return False, "FAIL - Original Exam_Score is missing (None)"

    if isinstance(exam_score, bool) or not isinstance(exam_score, (int, float)):
        return False, f"FAIL - Original Exam_Score must be numeric, got {type(exam_score).__name__}"

    if exam_score < 0 or exam_score > 100:
        return False, f"FAIL - Exam_Score must be between 0 and 100, got {exam_score}"

    return True, "PASS"


def validate_attendance(student):
    """
    Validates that attendance is numeric and between 0 and 100 inclusive.
    
    Parameters:
        student (dict): Student dictionary.
        
    Returns:
        tuple: (bool, str) -> (is_valid, message)
    """
    if not isinstance(student, dict):
        return False, "FAIL - Student record must be a dictionary"

    attendance = student.get("Attendance")
    if attendance is None:
        return False, "FAIL - Attendance is missing (None)"

    if isinstance(attendance, bool) or not isinstance(attendance, (int, float)):
        return False, f"FAIL - Attendance must be numeric, got {type(attendance).__name__}"

    if attendance < 0 or attendance > 100:
        return False, f"FAIL - Attendance must be between 0 and 100, got {attendance}"

    return True, "PASS"


def validate_income(student):
    """
    Validates Demo_Family_Income: must be numeric and non-negative (>= 0 in INR).
    Kept separate from the original Kaggle categorical Family_Income.
    
    Parameters:
        student (dict): Student dictionary.
        
    Returns:
        tuple: (bool, str) -> (is_valid, message)
    """
    if not isinstance(student, dict):
        return False, "FAIL - Student record must be a dictionary"

    income = student.get("Demo_Family_Income")
    if income is None:
        return False, "FAIL - Demo_Family_Income is missing (None)"

    if isinstance(income, bool) or not isinstance(income, (int, float)):
        return False, f"FAIL - Family Income must be numeric, got {type(income).__name__}"

    if income < 0:
        return False, f"FAIL - Family Income cannot be negative, got ₹{income:,}"

    return True, "PASS"


def validate_kaggle_family_income(student):
    """
    Validates the original Kaggle Family_Income categorical field separately.
    Accepts only 'Low', 'Medium', or 'High'.
    
    Parameters:
        student (dict): Student dictionary.
        
    Returns:
        tuple: (bool, str) -> (is_valid, message)
    """
    if not isinstance(student, dict):
        return False, "FAIL - Student record must be a dictionary"

    income_cat = student.get("Family_Income")
    if income_cat is None:
        return False, "FAIL - Original Family_Income category is missing (None)"

    if not isinstance(income_cat, str):
        return False, f"FAIL - Original Family_Income must be text, got {type(income_cat).__name__}"

    allowed_categories = ["Low", "Medium", "High"]
    cleaned_cat = income_cat.strip().capitalize()
    if cleaned_cat not in allowed_categories:
        return False, f"FAIL - Original Family_Income must be 'Low', 'Medium', or 'High', got '{income_cat}'"

    return True, "PASS"


def validate_backlogs(student):
    """
    Validates that academic backlogs is an integer and non-negative (>= 0).
    
    Parameters:
        student (dict): Student dictionary.
        
    Returns:
        tuple: (bool, str) -> (is_valid, message)
    """
    if not isinstance(student, dict):
        return False, "FAIL - Student record must be a dictionary"

    backlogs = student.get("Demo_Backlogs")
    if backlogs is None:
        return False, "FAIL - Backlogs count is missing (None)"

    # Backlogs must specifically be an integer, not float, bool, or string
    if isinstance(backlogs, bool) or not isinstance(backlogs, int):
        return False, f"FAIL - Backlogs must be an integer, got {type(backlogs).__name__}"

    if backlogs < 0:
        return False, f"FAIL - Backlogs cannot be negative, got {backlogs}"

    return True, "PASS"


def validate_enrollment(student):
    """
    Validates that enrollment status is either 'Active' or 'Inactive'.
    
    Parameters:
        student (dict): Student dictionary.
        
    Returns:
        tuple: (bool, str) -> (is_valid, message)
    """
    if not isinstance(student, dict):
        return False, "FAIL - Student record must be a dictionary"

    status = student.get("Demo_Enrollment_Status")
    if status is None:
        return False, "FAIL - Enrollment status is missing (None)"

    if not isinstance(status, str):
        return False, f"FAIL - Enrollment status must be text, got {type(status).__name__}"

    allowed = ["Active", "Inactive"]
    if status.strip().capitalize() not in allowed:
        return False, f"FAIL - Enrollment must be 'Active' or 'Inactive', got '{status}'"

    return True, "PASS"


def validate_extracurricular(student):
    """
    Validates that extracurricular activity status is either 'Yes' or 'No'.
    
    Parameters:
        student (dict): Student dictionary.
        
    Returns:
        tuple: (bool, str) -> (is_valid, message)
    """
    if not isinstance(student, dict):
        return False, "FAIL - Student record must be a dictionary"

    extra = student.get("Extracurricular_Activities")
    if extra is None:
        return False, "FAIL - Extracurricular activity is missing (None)"

    if not isinstance(extra, str):
        return False, f"FAIL - Extracurricular must be text, got {type(extra).__name__}"

    allowed = ["Yes", "No"]
    if extra.strip().capitalize() not in allowed:
        return False, f"FAIL - Extracurricular must be 'Yes' or 'No', got '{extra}'"

    return True, "PASS"


# =============================================================================
# MASTER RECORD VALIDATION
# =============================================================================

def validate_student(student):
    """
    Orchestrates complete validation for a student record by calling each
    individual field validator.
    
    Validates:
    - Student ID (non-empty)
    - Student Name (non-empty)
    - Demo_CGPA (0.0 to 10.0)
    - Original Exam_Score (0 to 100)
    - Attendance (0 to 100)
    - Demo_Family_Income (numeric >= 0)
    - Original Family_Income category ('Low', 'Medium', 'High')
    - Demo_Backlogs (integer >= 0)
    - Demo_Enrollment_Status ('Active' or 'Inactive')
    - Extracurricular Activities ('Yes' or 'No')
    
    Parameters:
        student (dict): Student record dictionary.
        
    Returns:
        dict: A comprehensive validation summary containing:
              - 'student_id': str
              - 'student_name': str
              - 'is_valid': bool
              - 'details': dict mapping rule name to (bool, message)
              - 'errors': list of failure reasons
    """
    checks = {
        "Student ID": validate_student_id(student),
        "Student Name": validate_student_name(student),
        "CGPA": validate_cgpa(student),
        "Exam Score": validate_exam_score(student),
        "Attendance": validate_attendance(student),
        "Income": validate_income(student),
        "Family Income Category": validate_kaggle_family_income(student),
        "Backlog": validate_backlogs(student),
        "Enrollment": validate_enrollment(student),
        "Extracurricular": validate_extracurricular(student)
    }

    errors = []
    for check_name, (is_ok, msg) in checks.items():
        if not is_ok:
            errors.append(f"{check_name}: {msg}")

    is_valid = len(errors) == 0
    sid = student.get("Student_ID", "UNKNOWN") if isinstance(student, dict) else "INVALID_RECORD"
    sname = student.get("Student_Name", student.get("Name", "UNKNOWN")) if isinstance(student, dict) else "INVALID_RECORD"

    return {
        "student_id": sid,
        "student_name": sname,
        "is_valid": is_valid,
        "details": checks,
        "errors": errors
    }


def display_validation_results(student):
    """
    Displays the structured validation report for a student record in the
    required clean format.
    
    Parameters:
        student (dict): Student record dictionary.
    """
    report = validate_student(student)
    sid = report["student_id"]
    sname = report["student_name"]
    details = report["details"]
    overall_status = "VALID" if report["is_valid"] else "INVALID"

    print("=" * 50)
    print("STUDENT DATA VALIDATION")
    print("=" * 50)
    print(f"Student ID: {sid}")
    print(f"Student Name: {sname}\n")

    # Display validation checks in a clear, consistent structure
    display_fields = [
        ("Student Name", "Student Name Validation"),
        ("CGPA", "CGPA Validation"),
        ("Exam Score", "Exam Score Validation"),
        ("Attendance", "Attendance Validation"),
        ("Income", "Income Validation"),
        ("Family Income Category", "Family Income Category Validation"),
        ("Backlog", "Backlog Validation"),
        ("Enrollment", "Enrollment Validation")
    ]

    for field_key, label in display_fields:
        is_ok, msg = details.get(field_key, (False, "FAIL - Missing check"))
        status_text = "PASS" if is_ok else msg
        print(f"{label}: {status_text}")

    print(f"\nOverall Data Status: {overall_status}")

    # If invalid, list exact failure reasons
    if not report["is_valid"]:
        print("\nReason(s) for Data Invalidation:")
        for err in report["errors"]:
            print(f"  • {err}")
    print("=" * 50)


# =============================================================================
# TEST HARNESS INCLUDING ALL 3 CORRECTIONS
# =============================================================================

def run_test_cases():
    """
    Executes the comprehensive test harness including the original 5 test cases
    plus the 3 new test cases for the requested corrections:
    1. Completely valid student.
    2. CGPA outside valid range (Demo_CGPA = 11.50).
    3. Attendance greater than 100 (Attendance = 108).
    4. Negative family income (Demo_Family_Income = -₹50,000).
    5. Missing student ID (Student_ID = "").
    6. [CORRECTION 1 TEST] Missing or blank student name.
    7. [CORRECTION 2 TEST] Invalid original Kaggle Family_Income category ('Extremely High').
    8. [CORRECTION 3 TEST] Original Exam_Score outside 0-100 scale (Exam_Score = 101).
    """
    print("\n" + "#" * 60)
    print(" PHASE 2: COMPREHENSIVE VALIDATION MODULE TEST HARNESS")
    print("#" * 60)

    test_cases = [
        # --- Existing Baseline Tests ---
        {
            "test_num": 1,
            "title": "Completely Valid Student (Typical Passing Record)",
            "data": {
                "Student_ID": "STU0001",
                "Student_Name": "Student_0001",
                "Exam_Score": 67,
                "Demo_CGPA": 6.70,
                "Attendance": 84,
                "Family_Income": "Low",
                "Demo_Family_Income": 200000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "No"
            }
        },
        {
            "test_num": 2,
            "title": "CGPA Outside Valid Range (Demo_CGPA = 11.50 > 10.0)",
            "data": {
                "Student_ID": "STU0002",
                "Student_Name": "Student_0002",
                "Exam_Score": 95,
                "Demo_CGPA": 11.50,
                "Attendance": 90,
                "Family_Income": "Medium",
                "Demo_Family_Income": 300000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes"
            }
        },
        {
            "test_num": 3,
            "title": "Attendance Greater Than 100 (Attendance = 108 > 100)",
            "data": {
                "Student_ID": "STU0003",
                "Student_Name": "Student_0003",
                "Exam_Score": 75,
                "Demo_CGPA": 7.50,
                "Attendance": 108,
                "Family_Income": "Medium",
                "Demo_Family_Income": 250000,
                "Demo_Backlogs": 1,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes"
            }
        },
        {
            "test_num": 4,
            "title": "Negative Family Income (Demo_Family_Income = -₹50,000 < 0)",
            "data": {
                "Student_ID": "STU0004",
                "Student_Name": "Student_0004",
                "Exam_Score": 82,
                "Demo_CGPA": 8.20,
                "Attendance": 92,
                "Family_Income": "Low",
                "Demo_Family_Income": -50000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "No"
            }
        },
        {
            "test_num": 5,
            "title": "Missing Student ID (Student_ID = '' / empty string)",
            "data": {
                "Student_ID": "",
                "Student_Name": "Student_0005",
                "Exam_Score": 70,
                "Demo_CGPA": 7.00,
                "Attendance": 85,
                "Family_Income": "Medium",
                "Demo_Family_Income": 220000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes"
            }
        },
        # --- Three New Tests for Requested Corrections ---
        {
            "test_num": 6,
            "title": "[CORRECTION 1] Missing / Blank Student Name (Student_Name = '')",
            "data": {
                "Student_ID": "STU0006",
                "Student_Name": "",  # Blank student name
                "Exam_Score": 88,
                "Demo_CGPA": 8.80,
                "Attendance": 92,
                "Family_Income": "Medium",
                "Demo_Family_Income": 450000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes"
            }
        },
        {
            "test_num": 7,
            "title": "[CORRECTION 2] Invalid Kaggle Family_Income Category ('Extremely High')",
            "data": {
                "Student_ID": "STU0007",
                "Student_Name": "Student_0007",
                "Exam_Score": 78,
                "Demo_CGPA": 7.80,
                "Attendance": 88,
                "Family_Income": "Extremely High",  # Invalid original category
                "Demo_Family_Income": 800000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "No"
            }
        },
        {
            "test_num": 8,
            "title": "[CORRECTION 3] Exam_Score Outside 0 to 100 Scale (Exam_Score = 101 > 100)",
            "data": {
                "Student_ID": "STU0008",
                "Student_Name": "Student_0008",
                "Exam_Score": 101,  # Greater than documented 100-point scale
                "Demo_CGPA": 10.00,
                "Attendance": 95,
                "Family_Income": "Low",
                "Demo_Family_Income": 200000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes"
            }
        }
    ]

    for tc in test_cases:
        print(f"\n--- [TEST CASE {tc['test_num']}: {tc['title']}] ---")
        display_validation_results(tc["data"])


def test_with_real_dataset():
    """
    Loads prepared records from data_loader.py and runs validation
    across all loaded records to verify end-to-end dataset integrity.
    """
    print("\n" + "=" * 60)
    print("VERIFYING FULL DATASET INTEGRITY VIA DATA_LOADER")
    print("=" * 60)

    try:
        students = load_students()
        total = len(students)
        valid_count = 0
        invalid_count = 0
        anomaly_list = []

        for s in students:
            res = validate_student(s)
            if res["is_valid"]:
                valid_count += 1
            else:
                invalid_count += 1
                anomaly_list.append((res["student_id"], res["errors"]))

        print(f"Total Loaded Records Checked : {total}")
        print(f"Valid Records Passed         : {valid_count} ({(valid_count/total)*100:.2f}%)")
        print(f"Invalid Records Flagged      : {invalid_count} ({(invalid_count/total)*100:.2f}%)")

        if anomaly_list:
            print("\nFlagged Anomaly Details in Kaggle Dataset:")
            for sid, errs in anomaly_list:
                print(f"  • Student [{sid}]: {', '.join(errs)}")
            print(">> Note: Validation successfully identified out-of-scale data in original Kaggle CSV!")
        else:
            print(">> All records passed validation!")
    except Exception as e:
        print(f"[NOTE] Could not load dataset directly: {e}")


if __name__ == "__main__":
    # 1. Run all test cases (including the 3 new corrections)
    run_test_cases()

    # 2. Verify dataset pipeline
    test_with_real_dataset()
