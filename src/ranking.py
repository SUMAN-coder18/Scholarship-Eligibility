"""
Scholarship Eligibility Screening System
Module: ranking.py
Phase: 6 - Merit Ranking and Tie-Breaking Module

Description:
    This module implements a deterministic multi-level ranking and tie-breaking
    engine for scholarship candidates. It processes evaluated student records
    from Phases 3-5 (eligibility.py) and ranks eligible applicants within their
    respective categories and across the entire institution.

===============================================================================
OFFICIAL MERIT-LIST & TIE-BREAKING POLICY:
===============================================================================
1. Overall Institutional Priority by Category Tier:
   - Tier 1: Highly Eligible candidates rank first.
   - Tier 2: Eligible candidates rank second.
   - Tier 3: Conditionally Eligible candidates rank third (audited exceptions).

2. Within each category tier, the four-level tie-breaking hierarchy applies:
   - Priority 1: Higher CGPA ranks first (Descending).
   - Priority 2: If CGPA is equal, higher Attendance ranks first (Descending).
   - Priority 3: If CGPA & Attendance are equal, lower Family Income ranks first
                 (Ascending -> higher financial need prioritized).
   - Priority 4: If all three values are equal, Student ID in alphabetical
                 order (Ascending -> STU0001 < STU0002 for deterministic stability).

3. Strict Exclusions:
   - Not Eligible students are strictly excluded from all merit lists.
   - Invalid Record students are strictly excluded from all merit lists.

Author: BCA Student Developer
Advisor: Senior Python Developer & Mentor
"""

import os
import sys
import hashlib
import csv

# Ensure local 'src' directory can be imported
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
# DEFENSIVE VALUE EXTRACTORS
# =============================================================================

def get_cgpa(record):
    """
    Safely extracts the Demo_CGPA float from an evaluated or raw student record.
    """
    if "Demo_CGPA" in record and record["Demo_CGPA"] is not None:
        return float(record["Demo_CGPA"])
    return float(record.get("checks", {}).get("academic", {}).get("cgpa", 0.0) or 0.0)


def get_attendance(record):
    """
    Safely extracts the Attendance float from an evaluated or raw student record.
    """
    if "Attendance" in record and record["Attendance"] is not None:
        return float(record["Attendance"])
    return float(record.get("checks", {}).get("attendance", {}).get("attendance", 0.0) or 0.0)


def get_income(record):
    """
    Safely extracts the Demo_Family_Income integer from a student record.
    """
    if "Demo_Family_Income" in record and record["Demo_Family_Income"] is not None:
        return int(record["Demo_Family_Income"])
    return int(record.get("checks", {}).get("income", {}).get("income", 0) or 0)


def get_student_id(record):
    """
    Safely extracts the Student_ID string from a student record.
    """
    return str(record.get("student_id", record.get("Student_ID", "")))


def get_student_name(record):
    """
    Safely extracts the Student_Name string from a student record.
    """
    return str(record.get("student_name", record.get("Student_Name", "Unknown")))


def get_classification(record):
    """
    Safely extracts the classification string from an evaluation record.
    """
    return str(record.get("classification", ""))


def get_eligibility_score(record):
    """
    Safely extracts the composite eligibility score (0.0 to 100.0) from a student record.
    """
    score_data = record.get("eligibility_score")
    if isinstance(score_data, dict):
        return float(score_data.get("total_score", 0.0))
    if score_data is not None:
        try:
            return float(score_data)
        except (ValueError, TypeError):
            pass
    return 0.0


# =============================================================================
# REQUIRED RANKING FUNCTIONS
# =============================================================================

def filter_eligible_students(evaluated_students):
    """
    Filters out any student records that are Not Eligible or have Invalid Data.
    Only students classified as Highly Eligible, Eligible, or Conditionally
    Eligible are retained for scholarship merit ranking.
    
    Parameters:
        evaluated_students (list): List of evaluated student profile dictionaries.
        
    Returns:
        list: Filtered list containing only eligible, valid candidates.
    """
    allowed_categories = ["Highly Eligible", "Eligible", "Conditionally Eligible"]
    eligible_students = []

    # Iterate through all evaluations and retain only valid eligible records
    for student in evaluated_students:
        is_valid = student.get("is_valid_data", True)
        is_eligible = student.get("is_eligible", False)
        classification = get_classification(student)

        # Student must be structurally valid, marked eligible, and in an allowed category
        if is_valid and is_eligible and classification in allowed_categories:
            eligible_students.append(student)

    return eligible_students


def rank_students(students_list):
    """
    Ranks a list of student records based on the four-level tie-breaking hierarchy:
    1. Primary Key    : CGPA (Descending -> Higher CGPA ranks higher)
    2. 1st Tie-Breaker: Attendance (Descending -> Higher attendance ranks higher)
    3. 2nd Tie-Breaker: Family Income (Ascending -> Lower income / higher need ranks higher)
    4. Final Tie-Break: Student ID (Ascending -> Alphabetical order for deterministic results)
    
    Explanation of Sorting Key:
    - Python's built-in sorted() compares multi-element tuples element-by-element
      from left to right.
    - To sort CGPA and Attendance in DESCENDING order, we negate their numerical
      values: -get_cgpa(s) and -get_attendance(s). For example, -9.5 is less than
      -8.0, so 9.5 appears first.
    - Family Income is left positive: get_income(s), so lower income appears first.
    - Student ID is compared as an ascending string: get_student_id(s).
    
    Parameters:
        students_list (list): List of student dictionaries to be ranked.
        
    Returns:
        list: Sorted list of students with an assigned 'rank' integer (1, 2, 3...).
    """
    # Guard clause: handle empty lists safely without exceptions
    if not students_list:
        return []

    # Multi-level sort using sorted() and lambda expression
    sorted_students = sorted(
        students_list,
        key=lambda s: (-get_cgpa(s), -get_attendance(s), get_income(s), get_student_id(s))
    )

    # Assign sequential ranks (1, 2, 3...)
    ranked_students = []
    for rank_number, student in enumerate(sorted_students, start=1):
        # Create a clean shallow copy so we do not mutate the input dictionary unexpectedly
        student_copy = dict(student)
        student_copy["rank"] = rank_number
        ranked_students.append(student_copy)

    return ranked_students


def rank_by_category(evaluated_students):
    """
    Groups eligible students by their classification category and applies
    merit ranking within each category separately.
    
    Categories Ranked:
    - Highly Eligible
    - Eligible
    - Conditionally Eligible
    
    Parameters:
        evaluated_students (list): List of evaluated student dictionaries.
        
    Returns:
        dict: Mapping category name to its ranked list of students.
              Example: {
                  "Highly Eligible": [ranked students...],
                  "Eligible": [ranked students...],
                  "Conditionally Eligible": [ranked students...]
              }
    """
    # 1. Filter out all ineligible and invalid records first
    eligible_candidates = filter_eligible_students(evaluated_students)

    # 2. Group candidates by category
    categories = ["Highly Eligible", "Eligible", "Conditionally Eligible"]
    grouped = {cat: [] for cat in categories}

    for student in eligible_candidates:
        cat = get_classification(student)
        if cat in grouped:
            grouped[cat].append(student)

    # 3. Apply rank_students() to each category group independently
    ranked_categories = {}
    for cat in categories:
        ranked_categories[cat] = rank_students(grouped[cat])

    return ranked_categories


def create_overall_merit_list(evaluated_students):
    """
    Constructs the consolidated institutional merit list using the documented policy:
    1. Highly Eligible candidates first (Tier 1)
    2. Eligible candidates second (Tier 2)
    3. Conditionally Eligible candidates third (Tier 3)
    4. Within each tier, apply the four ranking priorities:
       - Higher CGPA first (Descending)
       - Higher Attendance first (Descending)
       - Lower Family Income first (Ascending)
       - Student ID alphabetically (Ascending)
       
    Parameters:
        evaluated_students (list): Full list of student evaluations.
        
    Returns:
        list: Fully ranked overall merit list with 'rank' assigned from 1 to N.
    """
    all_eligible = filter_eligible_students(evaluated_students)

    category_order = {
        "Highly Eligible": 1,
        "Eligible": 2,
        "Conditionally Eligible": 3
    }

    # Combined sort: Primary by Category Tier, Secondary by Academic & Need Tie-Breakers
    overall_sorted = sorted(
        all_eligible,
        key=lambda s: (
            category_order.get(get_classification(s), 99),
            -get_cgpa(s),
            -get_attendance(s),
            get_income(s),
            get_student_id(s)
        )
    )

    overall_ranked = []
    for rnum, item in enumerate(overall_sorted, start=1):
        c = dict(item)
        c["rank"] = rnum
        overall_ranked.append(c)

    return overall_ranked


# =============================================================================
# FORMATTED OUTPUT FUNCTIONS
# =============================================================================

def display_ranked_students(ranked_students, category_name="SCHOLARSHIP MERIT LIST", limit=None):
    """
    Displays a formatted ASCII table of ranked students for a given category.
    
    Columns Displayed:
    - Rank number
    - Student ID
    - Student name
    - Scholarship classification
    - CGPA
    - Attendance
    - Annual family income
    
    Parameters:
        ranked_students (list): List of ranked student dictionaries.
        category_name (str): Name/Title of the category being displayed.
        limit (int, optional): Maximum number of rows to print.
    """
    print("\n" + "=" * 90)
    title_text = f"RANKED MERIT LIST: {category_name.upper()}"
    print(f" {title_text.center(88)} ")
    print("=" * 90)

    header = (
        f"{'Rank':<6} | {'Student ID':<10} | {'Student Name':<18} | "
        f"{'Classification':<22} | {'CGPA':<6} | {'Attnd':<6} | {'Income (INR)':<12}"
    )
    print(header)
    print("-" * 90)

    if not ranked_students:
        print("  (No eligible students found in this category)")
        print("=" * 90)
        return

    display_list = ranked_students[:limit] if limit is not None else ranked_students

    for s in display_list:
        rank_val = s.get("rank", "-")
        sid = get_student_id(s)
        sname = get_student_name(s)[:17]
        cls_name = get_classification(s)[:21]
        cgpa_val = get_cgpa(s)
        attnd_val = get_attendance(s)
        income_val = get_income(s)

        row_str = (
            f"#{rank_val:<5} | {sid:<10} | {sname:<18} | "
            f"{cls_name:<22} | {cgpa_val:<6.2f} | {attnd_val:<5.1f}% | ₹{income_val:<11,}"
        )
        print(row_str)

    print("-" * 90)
    if limit is not None and len(ranked_students) > limit:
        print(f"Showing Top {limit} of {len(ranked_students)} total ranked applicants in this category.")
    else:
        print(f"Total Ranked Students: {len(ranked_students)}")
    print("=" * 90)


def display_complete_merit_list(overall_ranked_students, limit=15):
    """
    Displays the consolidated institutional merit list of all eligible students,
    ranked across all three qualifying categories.
    
    Parameters:
        overall_ranked_students (list): Combined list of ranked eligible students.
        limit (int, optional): Maximum number of rows to print (default: 15).
    """
    print("\n" + "=" * 90)
    print(" COMPLETE INSTITUTIONAL SCHOLARSHIP MERIT LIST (ALL CATEGORIES) ".center(90, "="))
    print("=" * 90)

    header = (
        f"{'Rank':<6} | {'Student ID':<10} | {'Student Name':<18} | "
        f"{'Classification':<22} | {'CGPA':<6} | {'Attnd':<6} | {'Income (INR)':<12}"
    )
    print(header)
    print("-" * 90)

    if not overall_ranked_students:
        print("  (No eligible candidates on the merit list)")
        print("=" * 90)
        return

    display_list = overall_ranked_students[:limit] if limit is not None else overall_ranked_students

    for s in display_list:
        rank_val = s.get("rank", "-")
        sid = get_student_id(s)
        sname = get_student_name(s)[:17]
        cls_name = get_classification(s)[:21]
        cgpa_val = get_cgpa(s)
        attnd_val = get_attendance(s)
        income_val = get_income(s)

        row_str = (
            f"#{rank_val:<5} | {sid:<10} | {sname:<18} | "
            f"{cls_name:<22} | {cgpa_val:<6.2f} | {attnd_val:<5.1f}% | ₹{income_val:<11,}"
        )
        print(row_str)

    print("-" * 90)
    if limit is not None and len(overall_ranked_students) > limit:
        print(f"Showing Top {limit} of {len(overall_ranked_students)} total ranked candidates institution-wide.")
    else:
        print(f"Total Ranked Candidates: {len(overall_ranked_students)}")
    print("=" * 90)


# =============================================================================
# DATASET FILE INTEGRITY VERIFIER
# =============================================================================

def verify_original_csv_integrity(filepath="dataset/original_dataset.csv"):
    """
    Genuinely checks that the original Kaggle CSV file remains completely unchanged.
    
    Verifies:
    1. File existence.
    2. File size matches exact original byte length (641,949 bytes).
    3. SHA-256 cryptographic hash matches original pristine state:
       'e8df8c4148ef83fb295ca1c092f2c6ee15272c0a8e3018b769a788ab50e96e97'
    4. Row count matches exact original (6,608 total lines = 1 header + 6,607 data rows).
    
    Parameters:
        filepath (str): Relative path to original CSV file.
        
    Returns:
        bool: True if file is 100% untouched and verified.
    """
    if not os.path.exists(filepath):
        # Look relative to project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.normpath(os.path.join(script_dir, "..", "dataset", "original_dataset.csv"))

    assert os.path.exists(filepath), f"Integrity Failure: '{filepath}' does not exist!"

    # Read binary bytes
    with open(filepath, "rb") as f:
        file_bytes = f.read()

    actual_size = len(file_bytes)
    actual_hash = hashlib.sha256(file_bytes).hexdigest()

    expected_size = 641949
    expected_hash = "e8df8c4148ef83fb295ca1c092f2c6ee15272c0a8e3018b769a788ab50e96e97"

    # Assert exact byte size
    assert actual_size == expected_size, (
        f"Integrity Failure: File size changed! Expected {expected_size} bytes, got {actual_size} bytes."
    )

    # Assert exact cryptographic hash
    assert actual_hash == expected_hash, (
        f"Integrity Failure: SHA-256 checksum mismatch! File content was modified."
    )

    # Verify line count
    with open(filepath, "r", encoding="utf-8-sig") as f:
        total_lines = sum(1 for _ in f)

    assert total_lines == 6608, (
        f"Integrity Failure: Line count changed! Expected 6,608 lines, got {total_lines}."
    )

    return True, actual_size, actual_hash, total_lines


# =============================================================================
# COMPREHENSIVE TEST SUITE WITH ACTUAL PYTHON ASSERTS
# =============================================================================

def run_phase_6_tests():
    """
    Executes the eight mandatory test cases required for Phase 6 with explicit
    Python assert statements on all expected rankings, exclusions, and empty states:
    1. Different CGPA values.
    2. Equal CGPA but different attendance.
    3. Equal CGPA and attendance but different income.
    4. All three ranking values equal, using Student ID as final tie-breaker.
    5. Students from different eligibility categories.
    6. Not Eligible students excluded.
    7. Invalid records excluded.
    8. Empty eligible student list.
    """
    print("\n" + "#" * 65)
    print(" PHASE 6: MERIT RANKING AND TIE-BREAKING TEST HARNESS")
    print("#" * 65)

    # -------------------------------------------------------------------------
    # TEST 1: Different CGPA Values
    # -------------------------------------------------------------------------
    print("\n--- [TEST 1: Different CGPA Values (Higher CGPA Ranks Higher)] ---")
    test1_data = [
        {"Student_ID": "STU-01", "Student_Name": "Pooja", "Demo_CGPA": 7.80, "Attendance": 85.0, "Demo_Family_Income": 300000, "classification": "Eligible"},
        {"Student_ID": "STU-02", "Student_Name": "Amit", "Demo_CGPA": 9.40, "Attendance": 85.0, "Demo_Family_Income": 300000, "classification": "Eligible"},
        {"Student_ID": "STU-03", "Student_Name": "Rohan", "Demo_CGPA": 8.50, "Attendance": 85.0, "Demo_Family_Income": 300000, "classification": "Eligible"}
    ]
    ranked1 = rank_students(test1_data)
    display_ranked_students(ranked1, "Test 1 - Different CGPA")

    # Actual Python asserts
    expected_order_1 = ["STU-02", "STU-03", "STU-01"]
    actual_order_1 = [s["Student_ID"] for s in ranked1]
    assert actual_order_1 == expected_order_1, f"Test 1 Failed: Expected {expected_order_1}, got {actual_order_1}"
    assert [s["rank"] for s in ranked1] == [1, 2, 3], "Test 1 Failed: Ranks must be [1, 2, 3]"
    print(f"Assert Passed: Order is {actual_order_1} (Amit 9.40 -> Rohan 8.50 -> Pooja 7.80)")

    # -------------------------------------------------------------------------
    # TEST 2: Equal CGPA, Different Attendance
    # -------------------------------------------------------------------------
    print("\n--- [TEST 2: Equal CGPA, Different Attendance (Higher Attendance Ranks Higher)] ---")
    test2_data = [
        {"Student_ID": "STU-04", "Student_Name": "Kavita", "Demo_CGPA": 8.50, "Attendance": 82.0, "Demo_Family_Income": 300000, "classification": "Eligible"},
        {"Student_ID": "STU-05", "Student_Name": "Deepak", "Demo_CGPA": 8.50, "Attendance": 94.0, "Demo_Family_Income": 300000, "classification": "Eligible"},
        {"Student_ID": "STU-06", "Student_Name": "Alok", "Demo_CGPA": 8.50, "Attendance": 88.0, "Demo_Family_Income": 300000, "classification": "Eligible"}
    ]
    ranked2 = rank_students(test2_data)
    display_ranked_students(ranked2, "Test 2 - Equal CGPA, Different Attendance")

    # Actual Python asserts
    expected_order_2 = ["STU-05", "STU-06", "STU-04"]
    actual_order_2 = [s["Student_ID"] for s in ranked2]
    assert actual_order_2 == expected_order_2, f"Test 2 Failed: Expected {expected_order_2}, got {actual_order_2}"
    assert [s["rank"] for s in ranked2] == [1, 2, 3], "Test 2 Failed: Ranks must be [1, 2, 3]"
    print(f"Assert Passed: Order is {actual_order_2} (Deepak 94.0% -> Alok 88.0% -> Kavita 82.0%)")

    # -------------------------------------------------------------------------
    # TEST 3: Equal CGPA & Attendance, Different Income
    # -------------------------------------------------------------------------
    print("\n--- [TEST 3: Equal CGPA & Attendance, Different Income (Lower Income Ranks Higher)] ---")
    test3_data = [
        {"Student_ID": "STU-07", "Student_Name": "Vikram", "Demo_CGPA": 8.50, "Attendance": 90.0, "Demo_Family_Income": 450000, "classification": "Eligible"},
        {"Student_ID": "STU-08", "Student_Name": "Suresh", "Demo_CGPA": 8.50, "Attendance": 90.0, "Demo_Family_Income": 180000, "classification": "Eligible"},
        {"Student_ID": "STU-09", "Student_Name": "Meena", "Demo_CGPA": 8.50, "Attendance": 90.0, "Demo_Family_Income": 250000, "classification": "Eligible"}
    ]
    ranked3 = rank_students(test3_data)
    display_ranked_students(ranked3, "Test 3 - Equal CGPA & Attendance, Different Income")

    # Actual Python asserts
    expected_order_3 = ["STU-08", "STU-09", "STU-07"]
    actual_order_3 = [s["Student_ID"] for s in ranked3]
    assert actual_order_3 == expected_order_3, f"Test 3 Failed: Expected {expected_order_3}, got {actual_order_3}"
    assert [s["rank"] for s in ranked3] == [1, 2, 3], "Test 3 Failed: Ranks must be [1, 2, 3]"
    print(f"Assert Passed: Order is {actual_order_3} (Suresh ₹180k -> Meena ₹250k -> Vikram ₹450k)")

    # -------------------------------------------------------------------------
    # TEST 4: All Three Equal -> Student ID Final Tie-Breaker
    # -------------------------------------------------------------------------
    print("\n--- [TEST 4: All Three Equal -> Student ID Ascending Tie-Breaker] ---")
    test4_data = [
        {"Student_ID": "STU-Z99", "Student_Name": "Zoya", "Demo_CGPA": 8.50, "Attendance": 90.0, "Demo_Family_Income": 200000, "classification": "Eligible"},
        {"Student_ID": "STU-A01", "Student_Name": "Aarav", "Demo_CGPA": 8.50, "Attendance": 90.0, "Demo_Family_Income": 200000, "classification": "Eligible"},
        {"Student_ID": "STU-M50", "Student_Name": "Manoj", "Demo_CGPA": 8.50, "Attendance": 90.0, "Demo_Family_Income": 200000, "classification": "Eligible"}
    ]
    ranked4 = rank_students(test4_data)
    display_ranked_students(ranked4, "Test 4 - Student ID Tie-Breaker")

    # Actual Python asserts
    expected_order_4 = ["STU-A01", "STU-M50", "STU-Z99"]
    actual_order_4 = [s["Student_ID"] for s in ranked4]
    assert actual_order_4 == expected_order_4, f"Test 4 Failed: Expected {expected_order_4}, got {actual_order_4}"
    assert [s["rank"] for s in ranked4] == [1, 2, 3], "Test 4 Failed: Ranks must be [1, 2, 3]"
    print(f"Assert Passed: Order is {actual_order_4} (Aarav STU-A01 -> Manoj STU-M50 -> Zoya STU-Z99)")

    # -------------------------------------------------------------------------
    # TEST 5: Students From Different Eligibility Categories
    # -------------------------------------------------------------------------
    print("\n--- [TEST 5: Students From Different Eligibility Categories (Ranked By Category)] ---")
    test5_data = [
        {"Student_ID": "STU-H1", "Student_Name": "Hema", "Demo_CGPA": 8.90, "Attendance": 92.0, "Demo_Family_Income": 200000, "classification": "Highly Eligible", "is_valid_data": True, "is_eligible": True},
        {"Student_ID": "STU-H2", "Student_Name": "Harish", "Demo_CGPA": 8.60, "Attendance": 88.0, "Demo_Family_Income": 250000, "classification": "Highly Eligible", "is_valid_data": True, "is_eligible": True},
        {"Student_ID": "STU-E1", "Student_Name": "Ekta", "Demo_CGPA": 7.80, "Attendance": 80.0, "Demo_Family_Income": 350000, "classification": "Eligible", "is_valid_data": True, "is_eligible": True},
        {"Student_ID": "STU-E2", "Student_Name": "Eshan", "Demo_CGPA": 7.40, "Attendance": 82.0, "Demo_Family_Income": 400000, "classification": "Eligible", "is_valid_data": True, "is_eligible": True},
        {"Student_ID": "STU-C1", "Student_Name": "Chitra", "Demo_CGPA": 6.90, "Attendance": 85.0, "Demo_Family_Income": 200000, "classification": "Conditionally Eligible", "is_valid_data": True, "is_eligible": True},
        {"Student_ID": "STU-C2", "Student_Name": "Chetan", "Demo_CGPA": 6.80, "Attendance": 80.0, "Demo_Family_Income": 220000, "classification": "Conditionally Eligible", "is_valid_data": True, "is_eligible": True}
    ]
    by_category = rank_by_category(test5_data)
    for cat_name, cat_list in by_category.items():
        display_ranked_students(cat_list, cat_name)

    # Actual Python asserts
    assert len(by_category["Highly Eligible"]) == 2, "Test 5 Failed: Highly Eligible count should be 2"
    assert len(by_category["Eligible"]) == 2, "Test 5 Failed: Eligible count should be 2"
    assert len(by_category["Conditionally Eligible"]) == 2, "Test 5 Failed: Conditionally Eligible count should be 2"

    assert [s["Student_ID"] for s in by_category["Highly Eligible"]] == ["STU-H1", "STU-H2"]
    assert [s["Student_ID"] for s in by_category["Eligible"]] == ["STU-E1", "STU-E2"]
    assert [s["Student_ID"] for s in by_category["Conditionally Eligible"]] == ["STU-C1", "STU-C2"]
    print("Assert Passed: Category grouping and independent category ranks verified.")

    # -------------------------------------------------------------------------
    # TEST 6: Not Eligible Students Excluded
    # -------------------------------------------------------------------------
    print("\n--- [TEST 6: Not Eligible Students Excluded from Ranking] ---")
    test6_data = [
        {"Student_ID": "STU-OK1", "Student_Name": "Valid Student", "Demo_CGPA": 7.50, "Attendance": 80.0, "Demo_Family_Income": 300000, "classification": "Eligible", "is_valid_data": True, "is_eligible": True},
        {"Student_ID": "STU-NO1", "Student_Name": "Low Attendance", "Demo_CGPA": 8.50, "Attendance": 60.0, "Demo_Family_Income": 200000, "classification": "Not Eligible", "is_valid_data": True, "is_eligible": False},
        {"Student_ID": "STU-NO2", "Student_Name": "High Income", "Demo_CGPA": 8.80, "Attendance": 90.0, "Demo_Family_Income": 800000, "classification": "Not Eligible", "is_valid_data": True, "is_eligible": False}
    ]
    filtered6 = filter_eligible_students(test6_data)
    ranked6 = rank_students(filtered6)
    display_ranked_students(ranked6, "Test 6 - Exclude Ineligible")

    # Actual Python asserts
    assert len(filtered6) == 1, "Test 6 Failed: Ineligible students were not filtered out"
    assert len(ranked6) == 1, "Test 6 Failed: Ranked count should be 1"
    assert ranked6[0]["Student_ID"] == "STU-OK1", "Test 6 Failed: Expected STU-OK1"
    assert all(s["classification"] != "Not Eligible" for s in ranked6), "Test 6 Failed: Ineligible student in rank list"
    print("Assert Passed: Not Eligible candidates are 100% excluded from ranking.")

    # -------------------------------------------------------------------------
    # TEST 7: Invalid Records Excluded
    # -------------------------------------------------------------------------
    print("\n--- [TEST 7: Invalid Records Excluded from Ranking] ---")
    test7_data = [
        {"Student_ID": "STU-OK2", "Student_Name": "Valid Student 2", "Demo_CGPA": 7.60, "Attendance": 82.0, "Demo_Family_Income": 280000, "classification": "Eligible", "is_valid_data": True, "is_eligible": True},
        {"Student_ID": "STU-BAD1", "Student_Name": "", "Demo_CGPA": 11.50, "Attendance": 85.0, "Demo_Family_Income": 200000, "classification": "Invalid Record", "is_valid_data": False, "is_eligible": False}
    ]
    filtered7 = filter_eligible_students(test7_data)
    ranked7 = rank_students(filtered7)
    display_ranked_students(ranked7, "Test 7 - Exclude Invalid Records")

    # Actual Python asserts
    assert len(filtered7) == 1, "Test 7 Failed: Invalid records were not filtered out"
    assert len(ranked7) == 1, "Test 7 Failed: Ranked count should be 1"
    assert ranked7[0]["Student_ID"] == "STU-OK2", "Test 7 Failed: Expected STU-OK2"
    assert all(s["classification"] != "Invalid Record" for s in ranked7), "Test 7 Failed: Invalid record in rank list"
    print("Assert Passed: Invalid records are 100% excluded from ranking.")

    # -------------------------------------------------------------------------
    # TEST 8: Empty Eligible Student List
    # -------------------------------------------------------------------------
    print("\n--- [TEST 8: Empty Eligible Student List Handling] ---")
    empty_list = []
    ranked8 = rank_students(empty_list)
    display_ranked_students(ranked8, "Test 8 - Empty List")

    # Actual Python asserts
    assert ranked8 == [], "Test 8 Failed: Empty list should return empty list []"
    assert len(ranked8) == 0, "Test 8 Failed: Length must be 0"
    print("Assert Passed: Empty candidate list returns empty list without errors.")


# Alias for backward compatibility
run_phase_5_tests = run_phase_6_tests


def test_with_full_dataset():
    """
    Ranks the full Kaggle dataset evaluated through Phases 2, 3, 4, and 5.
    Verifies that:
    - Ranking order is strictly preserved.
    - No ineligible or invalid students are included.
    - The count of ranked candidates matches the number of eligible records.
    - Original CSV file remains 100% untouched.
    """
    print("\n" + "=" * 90)
    print(" EXECUTING PHASE 6 RANKING ON COMPLETE PREPARED DATASET ".center(90, "="))
    print("=" * 90)

    # Step A: Genuinely verify original CSV integrity before processing
    is_csv_valid, size, sha256_hash, lines = verify_original_csv_integrity()
    print("Original CSV Pre-Run Integrity Verification:")
    print(f"  • File Location  : dataset/original_dataset.csv")
    print(f"  • Exact Size     : {size:,} bytes")
    print(f"  • Total Lines    : {lines:,} (1 header + 6,607 records)")
    print(f"  • SHA-256 Hash   : {sha256_hash}")
    assert is_csv_valid, "Pre-run CSV integrity check failed!"
    print("  • Verification   : [PRISTINE & UNMODIFIED]")

    # Step B: Load and evaluate all students
    raw_students = load_students()
    evaluations = evaluate_all_students(raw_students)

    total_records = len(evaluations)
    valid_evaluations = [e for e in evaluations if e.get("is_valid_data", True)]
    eligible_count = sum(1 for e in valid_evaluations if e.get("is_eligible", False))

    print(f"\nTotal Student Profiles Evaluated : {total_records:,}")
    print(f"Total Eligible Candidates Found  : {eligible_count:,}")

    # Step C: Filter and rank by category
    ranked_by_cat = rank_by_category(evaluations)

    for cat_name, candidate_list in ranked_by_cat.items():
        display_ranked_students(candidate_list, cat_name, limit=5)

    # Step D: Construct Overall Institutional Merit List
    overall_ranked = create_overall_merit_list(evaluations)
    display_complete_merit_list(overall_ranked, limit=10)

    # Step E: Post-run Integrity and consistency verifications with asserts
    print("\nDATASET INTEGRITY & RANKING VERIFICATION REPORT:")
    total_ranked = len(overall_ranked)
    print(f"  • Total Candidates on Merit List : {total_ranked:,}")
    print(f"  • Total Eligible Candidates      : {eligible_count:,}")

    # Assert 1: Exact count match
    assert total_ranked == eligible_count, (
        f"Assertion Failed: Ranked count ({total_ranked}) does not match eligible count ({eligible_count})!"
    )
    print("  • Assert 1 Passed: Ranked count EXACTLY matches eligible count -> [PASSED]")

    # Assert 2: Zero ineligibles
    ineligible_in_rank = [
        s for s in overall_ranked
        if not s.get("is_eligible", False) or not s.get("is_valid_data", True) or s.get("classification") in ["Not Eligible", "Invalid Record"]
    ]
    assert len(ineligible_in_rank) == 0, (
        f"Assertion Failed: {len(ineligible_in_rank)} ineligible or invalid students found in merit list!"
    )
    print("  • Assert 2 Passed: Zero ineligible or invalid students on merit list -> [PASSED]")

    # Assert 3: Genuinely re-verify original CSV integrity after processing
    is_csv_valid_post, size_post, sha256_post, lines_post = verify_original_csv_integrity()
    assert is_csv_valid_post, "Post-run CSV integrity check failed!"
    assert size == size_post and sha256_hash == sha256_post and lines == lines_post, (
        "Assertion Failed: Original CSV was modified during program execution!"
    )
    print(f"  • Assert 3 Passed: Original CSV byte size ({size_post:,} bytes) and SHA-256 hash match 100% -> [PASSED]")
    print("=" * 90)


# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # 1. Run all 8 required unit test cases with Python asserts
    run_phase_6_tests()

    # 2. Run ranking on the full dataset with genuine integrity assertions
    test_with_full_dataset()
