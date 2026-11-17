"""
Scholarship Eligibility Screening System
Module: eligibility.py
Phases: 3, 4, 5 - Eligibility Checking, Classification & Scoring Engine

Description:
    This module implements the deterministic, rule-based screening engine.
    It integrates with validation.py to enforce data integrity, evaluates
    student profiles against five mandatory scholarship conditions, tracks
    additional considerations strictly using explicitly labeled demonstration
    fields without inferring values from Kaggle demographic attributes, and
    assigns applicants to one of four official screening classifications:
    1. Highly Eligible
    2. Eligible
    3. Conditionally Eligible (specific exception for CGPA 6.75 to 6.99)
    4. Not Eligible

Key Principles:
    - DATA INTEGRITY FIRST: Uses Phase 2 validate_student() as a mandatory gate.
      Invalid data records are never assigned a scholarship classification.
    - STRICT DEMONSTRATION PURITY: Never infers First-Generation status from
      Parental_Education_Level, nor general disability from Learning_Disabilities.
      Uses strictly 'Demo_First_Generation' and 'Demo_Disability_Status'.
      Returns 'Not Provided' if either field is missing.
    - STRICT DETERMINISM: Pure rule-based conditional logic; zero AI/ML or black boxes.
    - CORE PYTHON ONLY: Standard types, operators, and built-in modules only.

Author: BCA Student Developer
Advisor: Senior Python Developer & Mentor
"""

import os
import sys

# Ensure local 'src' directory can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from data_loader import load_students
    from validation import validate_student
except ImportError:
    from src.data_loader import load_students
    from src.validation import validate_student


# =============================================================================
# INDIVIDUAL MANDATORY RULE CHECKERS
# =============================================================================

def check_academic_eligibility(student):
    """
    Evaluates student CGPA against the standard and conditional cutoffs.
    
    Rules:
    - Standard Pass    : CGPA >= 7.00
    - Conditional Pass : 6.75 <= CGPA < 7.00 (Specific audited exception)
    - Fail             : CGPA < 6.75
    
    Parameters:
        student (dict): Student profile dictionary.
        
    Returns:
        dict: {
            "passed_standard": bool,
            "passed_conditional": bool,
            "cgpa": float,
            "message": str
        }
    """
    cgpa = student.get("Demo_CGPA")
    if cgpa is None:
        return {
            "passed_standard": False,
            "passed_conditional": False,
            "cgpa": None,
            "message": "CGPA is missing"
        }

    cgpa = float(cgpa)

    if cgpa >= 7.00:
        return {
            "passed_standard": True,
            "passed_conditional": False,
            "cgpa": cgpa,
            "message": f"CGPA {cgpa:.2f} meets the standard minimum (>= 7.00)"
        }
    elif 6.75 <= cgpa < 7.00:
        return {
            "passed_standard": False,
            "passed_conditional": True,
            "cgpa": cgpa,
            "message": f"CGPA {cgpa:.2f} qualifies under Conditional Exception (6.75 to 6.99)"
        }
    else:
        return {
            "passed_standard": False,
            "passed_conditional": False,
            "cgpa": cgpa,
            "message": f"CGPA {cgpa:.2f} is below the minimum threshold (requires >= 7.00, minimum 6.75 for exception)"
        }


def check_attendance_eligibility(student):
    """
    Evaluates student attendance percentage against the mandatory minimum (>= 75%).
    
    Parameters:
        student (dict): Student profile dictionary.
        
    Returns:
        dict: {
            "passed": bool,
            "attendance": float,
            "message": str
        }
    """
    attendance = student.get("Attendance")
    if attendance is None:
        return {
            "passed": False,
            "attendance": None,
            "message": "Attendance percentage is missing"
        }

    attendance = float(attendance)
    passed = attendance >= 75.0

    if passed:
        msg = f"Attendance {attendance:.1f}% satisfies the minimum requirement (>= 75%)"
    else:
        msg = f"Attendance {attendance:.1f}% is below the mandatory minimum (requires >= 75%)"

    return {
        "passed": passed,
        "attendance": attendance,
        "message": msg
    }


def check_income_eligibility(student):
    """
    Evaluates annual family income against the mandatory ceiling (<= ₹500,000).
    
    Parameters:
        student (dict): Student profile dictionary.
        
    Returns:
        dict: {
            "passed": bool,
            "income": int,
            "message": str
        }
    """
    income = student.get("Demo_Family_Income")
    if income is None:
        return {
            "passed": False,
            "income": None,
            "message": "Annual family income is missing"
        }

    income = int(income)
    passed = income <= 500000

    if passed:
        msg = f"Annual income ₹{income:,} is within the allowable limit (<= ₹500,000)"
    else:
        msg = f"Annual income ₹{income:,} exceeds the maximum income ceiling (<= ₹500,000)"

    return {
        "passed": passed,
        "income": income,
        "message": msg
    }


def check_backlog_eligibility(student):
    """
    Evaluates academic standing backlogs against the maximum allowable (<= 1).
    
    Parameters:
        student (dict): Student profile dictionary.
        
    Returns:
        dict: {
            "passed": bool,
            "backlogs": int,
            "message": str
        }
    """
    backlogs = student.get("Demo_Backlogs")
    if backlogs is None:
        return {
            "passed": False,
            "backlogs": None,
            "message": "Academic backlogs count is missing"
        }

    backlogs = int(backlogs)
    passed = backlogs <= 1

    if passed:
        msg = f"Active backlogs count ({backlogs}) satisfies condition (<= 1)"
    else:
        msg = f"Active backlogs count ({backlogs}) exceeds allowable limit (maximum 1)"

    return {
        "passed": passed,
        "backlogs": backlogs,
        "message": msg
    }


def check_enrollment(student):
    """
    Evaluates enrollment status: must be strictly 'Active'.
    
    Parameters:
        student (dict): Student profile dictionary.
        
    Returns:
        dict: {
            "passed": bool,
            "status": str,
            "message": str
        }
    """
    status = student.get("Demo_Enrollment_Status")
    if status is None:
        return {
            "passed": False,
            "status": None,
            "message": "Enrollment status is missing"
        }

    status_str = str(status).strip().capitalize()
    passed = status_str == "Active"

    if passed:
        msg = "Enrollment status is 'Active'"
    else:
        msg = f"Enrollment status is '{status}' (requires 'Active')"

    return {
        "passed": passed,
        "status": status,
        "message": msg
    }


# =============================================================================
# ADDITIONAL CONSIDERATIONS (REVIEWED & STRICTLY UN-INFERRED)
# =============================================================================

def parse_demo_indicator(value):
    """
    Parses an explicitly provided demonstration indicator value.
    Returns 'Yes', 'No', or 'Not Provided' if missing or None.
    
    Does NOT infer from any original Kaggle columns.
    
    Parameters:
        value: Any input value (bool, str, None).
        
    Returns:
        str: 'Yes', 'No', or 'Not Provided'.
    """
    if value is None or value == "":
        return "Not Provided"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    val_str = str(value).strip().capitalize()
    if val_str in ["Yes", "Y", "True"]:
        return "Yes"
    elif val_str in ["No", "N", "False"]:
        return "No"
    return "Not Provided"


def check_additional_considerations(student):
    """
    Tracks additional merit, demographic, and diversity considerations separately
    from mandatory conditions.
    
    Strict Rules Enforced:
    1. High Academic Distinction : CGPA >= 8.50
    2. Outstanding Attendance    : Attendance >= 90%
    3. Extracurricular Activity  : Extracurricular_Activities == 'Yes'
    4. First-Generation Status   : Uses ONLY 'Demo_First_Generation'.
       Never infers from Parental_Education_Level.
       If missing, returns 'Not Provided'.
    5. Disability Status         : Uses ONLY 'Demo_Disability_Status'.
       Never assumes Learning_Disabilities represents general disability.
       If missing, returns 'Not Provided'.
    6. First-Gen OR Disability   : Evaluates the logical OR between the two.
       If either is 'Yes', the combined status is 'Yes'.
       If both are 'No', the combined status is 'No'.
       If neither is 'Yes' and either is 'Not Provided', returns 'Not Provided'.
    
    Parameters:
        student (dict): Student profile dictionary.
        
    Returns:
        dict: Detailed dictionary of additional considerations.
    """
    cgpa = student.get("Demo_CGPA", 0.0) or 0.0
    attendance = student.get("Attendance", 0) or 0
    extra = str(student.get("Extracurricular_Activities", "")).strip().capitalize() == "Yes"

    # Strictly read explicitly labeled demonstration fields; never infer
    first_gen_raw = student.get("Demo_First_Generation")
    first_gen_status = parse_demo_indicator(first_gen_raw)

    disability_raw = student.get("Demo_Disability_Status")
    disability_status = parse_demo_indicator(disability_raw)

    # Evaluate the OR condition
    if first_gen_status == "Yes" or disability_status == "Yes":
        or_status = "Yes"
        or_condition_met = True
    elif first_gen_status == "No" and disability_status == "No":
        or_status = "No"
        or_condition_met = False
    else:
        # One or both are "Not Provided", and neither is "Yes"
        or_status = "Not Provided"
        or_condition_met = False

    return {
        "high_cgpa_distinction": cgpa >= 8.50,
        "outstanding_attendance": attendance >= 90.0,
        "extracurricular_achievement": extra,
        "first_gen_or_disability": or_condition_met,
        "details": {
            "cgpa_value": cgpa,
            "attendance_value": attendance,
            "extracurricular": "Yes" if extra else "No",
            "first_generation": first_gen_status,
            "disability_status": disability_status,
            "first_gen_or_disability": or_status
        }
    }


# =============================================================================
# DECISION EXPLANATION GENERATOR
# =============================================================================

def generate_explanation(student, evaluation_result):
    """
    Generates a concise, transparent, human-readable justification explaining
    why an applicant received their specific classification.
    
    Parameters:
        student (dict): Student record dictionary.
        evaluation_result (dict): Output from calculate_eligibility.
        
    Returns:
        str: Human-readable explanation.
    """
    sid = student.get("Student_ID", "UNKNOWN")
    sname = student.get("Student_Name", student.get("Name", "Applicant"))
    classification = evaluation_result.get("classification")

    if not evaluation_result.get("is_valid_data", True):
        errors_str = "; ".join(evaluation_result.get("validation_errors", []))
        return f"{sname} ({sid}): Disqualified from screening due to data integrity validation failure: [{errors_str}]."

    failed_reasons = evaluation_result.get("failed_reasons", [])
    checks = evaluation_result.get("checks", {})
    cgpa = checks.get("academic", {}).get("cgpa", 0.0)
    attendance = checks.get("attendance", {}).get("attendance", 0.0)

    if classification == "Highly Eligible":
        return (
            f"{sname} ({sid}) is classified as HIGHLY ELIGIBLE. "
            f"Satisfies all mandatory conditions with high academic distinction "
            f"(CGPA: {cgpa:.2f} >= 8.50) and outstanding attendance ({attendance:.1f}% >= 85%)."
        )
    elif classification == "Eligible":
        return (
            f"{sname} ({sid}) is classified as ELIGIBLE. "
            f"Satisfies all mandatory conditions (CGPA >= 7.00, Attendance >= 75%, "
            f"Income <= ₹500,000, Backlogs <= 1, Active enrollment)."
        )
    elif classification == "Conditionally Eligible":
        return (
            f"{sname} ({sid}) is classified as CONDITIONALLY ELIGIBLE. "
            f"Granted a specific academic exception: CGPA {cgpa:.2f} is between 6.75 and 6.99, "
            f"while satisfying all other mandatory criteria (Attendance, Income, Backlogs, Enrollment)."
        )
    else:  # Not Eligible
        reasons_text = "; ".join(failed_reasons)
        return (
            f"{sname} ({sid}) is classified as NOT ELIGIBLE. "
            f"Failed critical condition(s): [{reasons_text}]."
        )


# =============================================================================
# ELIGIBILITY SCORING ENGINE (COMPOSITE SCORE OUT OF 100)
# =============================================================================

def calculate_eligibility_score(student, evaluation_result=None):
    """
    Calculates a comprehensive scholarship eligibility score out of 100 points
    based on a transparent, multi-factor weighted formula:
    
    1. Academic Merit (CGPA)       : Max 40 Points -> (Demo_CGPA / 10.0) * 40.0
    2. Attendance Rate             : Max 30 Points -> (Attendance / 100.0) * 30.0
    3. Financial Need (Income)     : Max 20 Points ->
         - Income <= ₹200,000      : 20.0 Points (Highest Need)
         - ₹200,000 < Income <= ₹500,000 : 10.0 Points (Moderate Need)
         - Income > ₹500,000       :  0.0 Points (Above Threshold)
    4. Merit & Discipline Boost    : Max 10 Points ->
         - Extracurricular Activity: 5.0 Points (if 'Yes')
         - Clean Backlog Record    : 5.0 Points (if Backlogs == 0)
         
    Total Maximum Score: 100.00 Points
    
    Parameters:
        student (dict): Student profile dictionary.
        evaluation_result (dict, optional): Existing evaluation dictionary.
        
    Returns:
        dict: Detailed scoring dictionary with total_score and component breakdown.
    """
    # Guard against invalid data
    if evaluation_result and not evaluation_result.get("is_valid_data", True):
        return {
            "total_score": 0.0,
            "breakdown": {
                "academic_score": 0.0,
                "attendance_score": 0.0,
                "financial_score": 0.0,
                "merit_boost_score": 0.0
            }
        }

    # 1. Academic component (Max 40)
    cgpa = float(student.get("Demo_CGPA") or 0.0)
    academic_score = round(min(max(cgpa / 10.0, 0.0), 1.0) * 40.0, 2)

    # 2. Attendance component (Max 30)
    attendance = float(student.get("Attendance") or 0.0)
    attendance_score = round(min(max(attendance / 100.0, 0.0), 1.0) * 30.0, 2)

    # 3. Financial Need component (Max 20)
    income = student.get("Demo_Family_Income")
    if income is not None:
        try:
            income_num = float(income)
            if income_num <= 200000:
                financial_score = 20.0
            elif income_num <= 500000:
                financial_score = 10.0
            else:
                financial_score = 0.0
        except (ValueError, TypeError):
            financial_score = 0.0
    else:
        financial_score = 0.0

    # 4. Merit & Discipline Boost (Max 10)
    merit_boost = 0.0
    extra = str(student.get("Extracurricular_Activities", "")).strip().capitalize()
    if extra in ("Yes", "Y", "True"):
        merit_boost += 5.0

    backlogs = student.get("Demo_Backlogs")
    if backlogs is not None:
        try:
            if int(backlogs) == 0:
                merit_boost += 5.0
        except (ValueError, TypeError):
            pass

    total_score = round(academic_score + attendance_score + financial_score + merit_boost, 2)
    total_score = min(total_score, 100.00)

    return {
        "total_score": total_score,
        "breakdown": {
            "academic_score": academic_score,
            "attendance_score": attendance_score,
            "financial_score": financial_score,
            "merit_boost_score": merit_boost
        }
    }


# =============================================================================
# MASTER ELIGIBILITY ENGINE
# =============================================================================

def calculate_eligibility(student):
    """
    Orchestrates the complete eligibility screening process for a student record.
    
    Workflow:
    1. Validation Gate: Calls Phase 2 validate_student(student).
       If data is invalid, marks record invalid and assigns NO scholarship classification.
    2. Runs individual mandatory condition checkers:
       - Academic eligibility (CGPA >= 7.00, conditional 6.75 - 6.99)
       - Attendance eligibility (Attendance >= 75%)
       - Income eligibility (Income <= ₹500,000)
       - Backlog eligibility (Backlogs <= 1)
       - Enrollment status (Status == 'Active')
    3. Evaluates Classification:
       - Highly Eligible      : All mandatory pass AND CGPA >= 8.50 AND Attendance >= 85%.
       - Eligible             : All mandatory pass (but not Highly Eligible).
       - Conditionally Eligible: CGPA 6.75 to 6.99 AND all other 4 mandatory pass.
       - Not Eligible         : One or more applicable critical conditions fail.
    4. Evaluates additional considerations (tracked separately with Demo fields).
    5. Generates human-readable decision explanation.
    
    Parameters:
        student (dict): Student record dictionary.
        
    Returns:
        dict: Comprehensive screening evaluation dictionary.
    """
    # STEP 0: Data Validation Gate (Defensive Verification)
    val_report = validate_student(student)
    if not val_report.get("is_valid", False):
        result = {
            "student_id": student.get("Student_ID", "UNKNOWN"),
            "student_name": student.get("Student_Name", "UNKNOWN"),
            "is_valid_data": False,
            "classification": "Invalid Record",
            "is_eligible": False,
            "validation_errors": val_report.get("errors", []),
            "failed_reasons": ["Data validation failed"],
            "checks": {},
            "additional_considerations": {},
            "eligibility_score": {
                "total_score": 0.0,
                "breakdown": {
                    "academic_score": 0.0,
                    "attendance_score": 0.0,
                    "financial_score": 0.0,
                    "merit_boost_score": 0.0
                }
            }
        }
        result["explanation"] = generate_explanation(student, result)
        return result

    # STEP 1: Execute Mandatory Rules
    acad_check = check_academic_eligibility(student)
    att_check = check_attendance_eligibility(student)
    inc_check = check_income_eligibility(student)
    back_check = check_backlog_eligibility(student)
    enr_check = check_enrollment(student)

    # STEP 2: Determine Overall Eligibility and Classification
    other_conditions_pass = (
        att_check["passed"] and
        inc_check["passed"] and
        back_check["passed"] and
        enr_check["passed"]
    )

    failed_reasons = []
    if not att_check["passed"]:
        failed_reasons.append(att_check["message"])
    if not inc_check["passed"]:
        failed_reasons.append(inc_check["message"])
    if not back_check["passed"]:
        failed_reasons.append(back_check["message"])
    if not enr_check["passed"]:
        failed_reasons.append(enr_check["message"])

    # Classification logic:
    if acad_check["passed_standard"] and other_conditions_pass:
        cgpa_val = acad_check["cgpa"]
        att_val = att_check["attendance"]

        if cgpa_val >= 8.50 and att_val >= 85.0:
            classification = "Highly Eligible"
            is_eligible = True
        else:
            classification = "Eligible"
            is_eligible = True

    elif acad_check["passed_conditional"] and other_conditions_pass:
        classification = "Conditionally Eligible"
        is_eligible = True

    else:
        classification = "Not Eligible"
        is_eligible = False
        if not acad_check["passed_standard"] and not acad_check["passed_conditional"]:
            failed_reasons.insert(0, acad_check["message"])

    # STEP 3: Track Additional Considerations Separately
    additional_info = check_additional_considerations(student)

    # STEP 4: Calculate Composite Eligibility Score (Out of 100)
    score_info = calculate_eligibility_score(student)

    # STEP 5: Assemble Complete Evaluation Profile
    result = {
        "student_id": student.get("Student_ID", "UNKNOWN"),
        "student_name": student.get("Student_Name", "UNKNOWN"),
        "is_valid_data": True,
        "is_eligible": is_eligible,
        "classification": classification,
        "failed_reasons": failed_reasons,
        "checks": {
            "academic": acad_check,
            "attendance": att_check,
            "income": inc_check,
            "backlogs": back_check,
            "enrollment": enr_check
        },
        "additional_considerations": additional_info,
        "eligibility_score": score_info
    }

    result["explanation"] = generate_explanation(student, result)

    return result


def evaluate_all_students(students):
    """
    Evaluates a collection of students through the eligibility engine.
    
    Parameters:
        students (list): List of student dictionaries.
        
    Returns:
        list: List of evaluation result dictionaries.
    """
    return [calculate_eligibility(s) for s in students]


# =============================================================================
# FORMATTED OUTPUT & TEST HARNESS
# =============================================================================

def display_single_result(evaluation):
    """
    Displays a structured evaluation card for a student.
    
    Parameters:
        evaluation (dict): Output from calculate_eligibility.
    """
    sid = evaluation.get("student_id")
    sname = evaluation.get("student_name")
    classification = evaluation.get("classification")
    is_valid = evaluation.get("is_valid_data")
    score_info = evaluation.get("eligibility_score", {})
    total_score = score_info.get("total_score", 0.0)

    print("\n" + "=" * 65)
    print("SCHOLARSHIP ELIGIBILITY EVALUATION RESULT")
    print("=" * 65)
    print(f"Student ID        : {sid}")
    print(f"Student Name      : {sname}")
    print(f"Data Status       : {'VALID' if is_valid else 'INVALID'}")
    print(f"Classification    : {classification.upper()}")
    print(f"Eligibility Score : {total_score:.2f} / 100.00")

    if not is_valid:
        print("\nValidation Errors (Disqualified):")
        for err in evaluation.get("validation_errors", []):
            print(f"  • {err}")
    else:
        checks = evaluation.get("checks", {})
        breakdown = score_info.get("breakdown", {})

        print("\nEligibility Score Breakdown (Out of 100 Points):")
        print(f"  • Academic Merit (CGPA)       : {breakdown.get('academic_score', 0.0):.2f} / 40.00")
        print(f"  • Attendance Rate             : {breakdown.get('attendance_score', 0.0):.2f} / 30.00")
        print(f"  • Financial Need (Income)     : {breakdown.get('financial_score', 0.0):.2f} / 20.00")
        print(f"  • Merit & Discipline Boost    : {breakdown.get('merit_boost_score', 0.0):.2f} / 10.00")
        print(f"  Total Composite Score         : {total_score:.2f} / 100.00")

        print("\nMandatory Conditions Review:")
        
        # CGPA
        ac = checks.get("academic", {})
        ac_sym = "PASS" if ac.get("passed_standard") else ("CONDITIONAL PASS" if ac.get("passed_conditional") else "FAIL")
        print(f"  1. CGPA Check            : [{ac_sym:<16}] {ac.get('message')}")

        # Attendance
        at = checks.get("attendance", {})
        at_sym = "PASS" if at.get("passed") else "FAIL"
        print(f"  2. Attendance Check      : [{at_sym:<16}] {at.get('message')}")

        # Income
        inc = checks.get("income", {})
        inc_sym = "PASS" if inc.get("passed") else "FAIL"
        print(f"  3. Family Income Check   : [{inc_sym:<16}] {inc.get('message')}")

        # Backlogs
        bk = checks.get("backlogs", {})
        bk_sym = "PASS" if bk.get("passed") else "FAIL"
        print(f"  4. Backlogs Check        : [{bk_sym:<16}] {bk.get('message')}")

        # Enrollment
        en = checks.get("enrollment", {})
        en_sym = "PASS" if en.get("passed") else "FAIL"
        print(f"  5. Enrollment Status     : [{en_sym:<16}] {en.get('message')}")

        # Additional Considerations
        add = evaluation.get("additional_considerations", {}).get("details", {})
        print("\nAdditional Considerations (Tracked Separately):")
        print(f"  • CGPA >= 8.50 Distinction     : {'Yes' if evaluation['additional_considerations']['high_cgpa_distinction'] else 'No'}")
        print(f"  • Attendance >= 90% Outstanding: {'Yes' if evaluation['additional_considerations']['outstanding_attendance'] else 'No'}")
        print(f"  • Extracurricular Activity     : {add.get('extracurricular', 'No')}")
        print(f"  • Demo First-Generation        : {add.get('first_generation', 'Not Provided')}")
        print(f"  • Demo Disability Status       : {add.get('disability_status', 'Not Provided')}")
        print(f"  • First-Gen OR Disability Met  : {add.get('first_gen_or_disability', 'Not Provided')}")

    print("\nDecision Explanation:")
    print(f"  \"{evaluation.get('explanation')}\"")
    print("=" * 65)


def run_test_cases():
    """
    Executes the comprehensive Phases 3, 4, 5 test suite:
    Part A: The 8 Baseline Classification Test Cases
    Part B: Demonstration Fields Handling Tests (Explicit Yes/No vs Missing)
    Part C: Exact Threshold Boundary Tests (CGPA 6.75, 7.00, 8.50; Attendance 85%; Income 500k; Backlogs 1)
    """
    print("\n" + "#" * 65)
    print(" PHASES 3, 4, 5: COMPREHENSIVE SCHOLARSHIP ELIGIBILITY TEST SUITE")
    print("#" * 65)

    # -------------------------------------------------------------------------
    # PART A: THE 8 BASELINE CLASSIFICATION TEST CASES
    # -------------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("PART A: EIGHT CORE CLASSIFICATION TEST CASES")
    print("=" * 65)

    core_tests = [
        {
            "test_num": 1,
            "title": "Highly Eligible Student (CGPA >= 8.50, Attendance >= 85%)",
            "data": {
                "Student_ID": "STU1001",
                "Student_Name": "Aditya Sharma",
                "Demo_CGPA": 8.90,
                "Exam_Score": 89,
                "Attendance": 92,
                "Family_Income": "Low",
                "Demo_Family_Income": 200000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes",
                "Demo_First_Generation": "Yes",
                "Demo_Disability_Status": "No"
            }
        },
        {
            "test_num": 2,
            "title": "Eligible Student (Standard Passing Criteria Met)",
            "data": {
                "Student_ID": "STU1002",
                "Student_Name": "Pooja Verma",
                "Demo_CGPA": 7.60,
                "Exam_Score": 76,
                "Attendance": 80,
                "Family_Income": "Medium",
                "Demo_Family_Income": 450000,
                "Demo_Backlogs": 1,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "No",
                "Demo_First_Generation": "No",
                "Demo_Disability_Status": "No"
            }
        },
        {
            "test_num": 3,
            "title": "Conditionally Eligible Student (CGPA 6.85 is 6.75 - 6.99 Exception)",
            "data": {
                "Student_ID": "STU1003",
                "Student_Name": "Rahul Singh",
                "Demo_CGPA": 6.85,
                "Exam_Score": 68,
                "Attendance": 82,
                "Family_Income": "Low",
                "Demo_Family_Income": 250000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes",
                "Demo_First_Generation": "Yes",
                "Demo_Disability_Status": "No"
            }
        },
        {
            "test_num": 4,
            "title": "Not Eligible Due to Low Attendance (Attendance = 68% < 75%)",
            "data": {
                "Student_ID": "STU1004",
                "Student_Name": "Sneha Patel",
                "Demo_CGPA": 8.10,
                "Exam_Score": 81,
                "Attendance": 68,
                "Family_Income": "Low",
                "Demo_Family_Income": 220000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes",
                "Demo_First_Generation": "No",
                "Demo_Disability_Status": "No"
            }
        },
        {
            "test_num": 5,
            "title": "Not Eligible Due to High Family Income (Income = ₹750,000 > ₹500,000)",
            "data": {
                "Student_ID": "STU1005",
                "Student_Name": "Karan Mehta",
                "Demo_CGPA": 8.70,
                "Exam_Score": 87,
                "Attendance": 91,
                "Family_Income": "High",
                "Demo_Family_Income": 750000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "No",
                "Demo_First_Generation": "No",
                "Demo_Disability_Status": "No"
            }
        },
        {
            "test_num": 6,
            "title": "Not Eligible Due to Excessive Backlogs (Backlogs = 3 > 1)",
            "data": {
                "Student_ID": "STU1006",
                "Student_Name": "Manish Gupta",
                "Demo_CGPA": 7.40,
                "Exam_Score": 74,
                "Attendance": 80,
                "Family_Income": "Medium",
                "Demo_Family_Income": 400000,
                "Demo_Backlogs": 3,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "No",
                "Demo_First_Generation": "No",
                "Demo_Disability_Status": "No"
            }
        },
        {
            "test_num": 7,
            "title": "Not Eligible Due to Inactive Enrollment (Status = 'Inactive')",
            "data": {
                "Student_ID": "STU1007",
                "Student_Name": "Divya Nair",
                "Demo_CGPA": 8.40,
                "Exam_Score": 84,
                "Attendance": 88,
                "Family_Income": "Low",
                "Demo_Family_Income": 210000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Inactive",
                "Extracurricular_Activities": "Yes",
                "Demo_First_Generation": "Yes",
                "Demo_Disability_Status": "No"
            }
        },
        {
            "test_num": 8,
            "title": "Invalid Data Record (Out-of-Scale Exam_Score = 101 / Blank Name)",
            "data": {
                "Student_ID": "STU1008",
                "Student_Name": "",
                "Demo_CGPA": 7.50,
                "Exam_Score": 101,
                "Attendance": 85,
                "Family_Income": "Low",
                "Demo_Family_Income": 200000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes"
            }
        }
    ]

    for tc in core_tests:
        print(f"\n--- [TEST {tc['test_num']}: {tc['title']}] ---")
        eval_res = calculate_eligibility(tc["data"])
        display_single_result(eval_res)

    # -------------------------------------------------------------------------
    # PART B: DEMONSTRATION FIELDS HANDLING TESTS (CORRECTIONS 1-6)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("PART B: DEMONSTRATION FIELDS HANDLING TESTS (EXPLICIT VS MISSING)")
    print("=" * 65)

    demo_field_tests = [
        {
            "label": "Demo Fields Completely Missing (Must Return 'Not Provided')",
            "data": {
                "Student_ID": "STU-DEMO1",
                "Student_Name": "Demo Applicant One",
                "Demo_CGPA": 7.80,
                "Exam_Score": 78,
                "Attendance": 85,
                "Family_Income": "Low",
                "Demo_Family_Income": 200000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes"
                # Demo_First_Generation and Demo_Disability_Status are omitted
            }
        },
        {
            "label": "Explicitly Provided: First-Gen = 'Yes', Disability = 'No' (OR Met)",
            "data": {
                "Student_ID": "STU-DEMO2",
                "Student_Name": "Demo Applicant Two",
                "Demo_CGPA": 7.80,
                "Exam_Score": 78,
                "Attendance": 85,
                "Family_Income": "Low",
                "Demo_Family_Income": 200000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes",
                "Demo_First_Generation": "Yes",
                "Demo_Disability_Status": "No"
            }
        },
        {
            "label": "Explicitly Provided: First-Gen = 'No', Disability = 'No' (OR Not Met)",
            "data": {
                "Student_ID": "STU-DEMO3",
                "Student_Name": "Demo Applicant Three",
                "Demo_CGPA": 7.80,
                "Exam_Score": 78,
                "Attendance": 85,
                "Family_Income": "Low",
                "Demo_Family_Income": 200000,
                "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active",
                "Extracurricular_Activities": "Yes",
                "Demo_First_Generation": "No",
                "Demo_Disability_Status": "No"
            }
        }
    ]

    for dtest in demo_field_tests:
        print(f"\n--- [DEMO FIELD TEST: {dtest['label']}] ---")
        res = calculate_eligibility(dtest["data"])
        add = res["additional_considerations"]["details"]
        print(f"  • Student: {res['student_name']} ({res['student_id']})")
        print(f"  • Demo First-Generation Value : {add['first_generation']}")
        print(f"  • Demo Disability Status Value: {add['disability_status']}")
        print(f"  • Combined (First-Gen OR Dis) : {add['first_gen_or_disability']}")

    # -------------------------------------------------------------------------
    # PART C: EXACT THRESHOLD BOUNDARY TESTS
    # -------------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("PART C: EXACT THRESHOLD BOUNDARY TESTS")
    print("=" * 65)

    boundary_tests = [
        {
            "name": "Boundary 1: Exact CGPA = 6.75 (Lower Boundary of Conditional Exception)",
            "data": {
                "Student_ID": "STU-BND1", "Student_Name": "Boundary Candidate 1",
                "Demo_CGPA": 6.75, "Exam_Score": 68, "Attendance": 80,
                "Family_Income": "Low", "Demo_Family_Income": 250000, "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active", "Extracurricular_Activities": "No"
            },
            "expected": "Conditionally Eligible"
        },
        {
            "name": "Boundary 2: Exact CGPA = 7.00 (Lower Boundary of Standard Eligible)",
            "data": {
                "Student_ID": "STU-BND2", "Student_Name": "Boundary Candidate 2",
                "Demo_CGPA": 7.00, "Exam_Score": 70, "Attendance": 80,
                "Family_Income": "Low", "Demo_Family_Income": 250000, "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active", "Extracurricular_Activities": "No"
            },
            "expected": "Eligible"
        },
        {
            "name": "Boundary 3: Exact CGPA = 8.50 & Attendance = 85% (Lower Boundary of Highly Eligible)",
            "data": {
                "Student_ID": "STU-BND3", "Student_Name": "Boundary Candidate 3",
                "Demo_CGPA": 8.50, "Exam_Score": 85, "Attendance": 85,
                "Family_Income": "Low", "Demo_Family_Income": 250000, "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active", "Extracurricular_Activities": "Yes"
            },
            "expected": "Highly Eligible"
        },
        {
            "name": "Boundary 4: Exact Attendance = 85% with CGPA >= 8.50 (Highly Eligible Boundary)",
            "data": {
                "Student_ID": "STU-BND4", "Student_Name": "Boundary Candidate 4",
                "Demo_CGPA": 8.80, "Exam_Score": 88, "Attendance": 85,
                "Family_Income": "Low", "Demo_Family_Income": 250000, "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active", "Extracurricular_Activities": "No"
            },
            "expected": "Highly Eligible"
        },
        {
            "name": "Boundary 5: Exact Income = ₹500,000 (Upper Ceiling Boundary of Family Income)",
            "data": {
                "Student_ID": "STU-BND5", "Student_Name": "Boundary Candidate 5",
                "Demo_CGPA": 7.50, "Exam_Score": 75, "Attendance": 80,
                "Family_Income": "Medium", "Demo_Family_Income": 500000, "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active", "Extracurricular_Activities": "No"
            },
            "expected": "Eligible"
        },
        {
            "name": "Boundary 6: Exact Backlogs = 1 (Upper Ceiling Boundary of Backlogs)",
            "data": {
                "Student_ID": "STU-BND6", "Student_Name": "Boundary Candidate 6",
                "Demo_CGPA": 7.50, "Exam_Score": 75, "Attendance": 80,
                "Family_Income": "Low", "Demo_Family_Income": 300000, "Demo_Backlogs": 1,
                "Demo_Enrollment_Status": "Active", "Extracurricular_Activities": "No"
            },
            "expected": "Eligible"
        }
    ]

    for btest in boundary_tests:
        res = calculate_eligibility(btest["data"])
        actual = res["classification"]
        status = "PASSED" if actual == btest["expected"] else "FAILED"
        print(f"\n--- [{btest['name']}] ---")
        print(f"  • Tested Value     : {btest['data'].get('Demo_CGPA', '')} CGPA, {btest['data'].get('Attendance', '')}% Attnd, ₹{btest['data'].get('Demo_Family_Income', ''):,} Income, {btest['data'].get('Demo_Backlogs', '')} Bklg")
        print(f"  • Classification   : {actual} (Expected: {btest['expected']}) -> [{status}]")
        print(f"  • Justification    : {res['explanation']}")

    # -------------------------------------------------------------------------
    # PART D: PHASE 5 ELIGIBILITY SCORING TESTS (OUT OF 100)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("PART D: ELIGIBILITY SCORING ENGINE TESTS (OUT OF 100 POINTS)")
    print("=" * 65)

    scoring_tests = [
        {
            "name": "Score Test 1: Perfect 100-Point Candidate",
            "data": {
                "Student_ID": "STU-SCR1", "Student_Name": "Perfect Scholar",
                "Demo_CGPA": 10.0, "Exam_Score": 100, "Attendance": 100,
                "Family_Income": "Low", "Demo_Family_Income": 150000, "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active", "Extracurricular_Activities": "Yes"
            },
            "expected_score": 100.00
        },
        {
            "name": "Score Test 2: Standard Baseline Qualifying Candidate",
            "data": {
                "Student_ID": "STU-SCR2", "Student_Name": "Baseline Scholar",
                "Demo_CGPA": 7.00, "Exam_Score": 70, "Attendance": 75,
                "Family_Income": "Medium", "Demo_Family_Income": 450000, "Demo_Backlogs": 1,
                "Demo_Enrollment_Status": "Active", "Extracurricular_Activities": "No"
            },
            "expected_score": 60.50  # 28.0 (CGPA) + 22.5 (Attnd) + 10.0 (Income) + 0.0 (Extra) + 0.0 (Backlog 1) = 60.50
        },
        {
            "name": "Score Test 3: Invalid Candidate Score Shielding",
            "data": {
                "Student_ID": "STU-SCR3", "Student_Name": "Invalid Scholar",
                "Demo_CGPA": 10.0, "Exam_Score": 101, "Attendance": 95,
                "Family_Income": "Low", "Demo_Family_Income": 200000, "Demo_Backlogs": 0,
                "Demo_Enrollment_Status": "Active", "Extracurricular_Activities": "Yes"
            },
            "expected_score": 0.00
        }
    ]

    for stest in scoring_tests:
        res = calculate_eligibility(stest["data"])
        actual_score = res.get("eligibility_score", {}).get("total_score", 0.0)
        assert actual_score == stest["expected_score"], f"Score mismatch: got {actual_score}, expected {stest['expected_score']}"
        print(f"\n--- [{stest['name']}] ---")
        print(f"  • Calculated Score : {actual_score:.2f} / 100.00 (Expected: {stest['expected_score']:.2f}) -> [PASSED]")
        bd = res.get("eligibility_score", {}).get("breakdown", {})
        print(f"    - CGPA: {bd.get('academic_score', 0):.2f}/40 | Attnd: {bd.get('attendance_score', 0):.2f}/30 | Income: {bd.get('financial_score', 0):.2f}/20 | Boost: {bd.get('merit_boost_score', 0):.2f}/10")


def run_dataset_screening_summary():
    """
    Runs the eligibility engine across the entire prepared dataset
    to verify real-world distribution and performance.
    """
    print("\n" + "=" * 65)
    print("RUNNING SCHOLARSHIP SCREENING ENGINE ON FULL PREPARED DATASET")
    print("=" * 65)

    students = load_students()
    evaluations = evaluate_all_students(students)

    total = len(evaluations)
    invalid_data_count = sum(1 for e in evaluations if not e["is_valid_data"])
    valid_evaluations = [e for e in evaluations if e["is_valid_data"]]

    highly_eligible = sum(1 for e in valid_evaluations if e["classification"] == "Highly Eligible")
    eligible = sum(1 for e in valid_evaluations if e["classification"] == "Eligible")
    conditionally_eligible = sum(1 for e in valid_evaluations if e["classification"] == "Conditionally Eligible")
    not_eligible = sum(1 for e in valid_evaluations if e["classification"] == "Not Eligible")

    total_eligible = highly_eligible + eligible + conditionally_eligible

    print(f"\nTotal Records Evaluated     : {total}")
    print(f"Data Validation Discrepancy : {invalid_data_count} (Exempted from screening)")
    print(f"Total Eligible Candidates   : {total_eligible} ({(total_eligible/total)*100:.2f}%)")
    print(f"  • Highly Eligible         : {highly_eligible:>4} ({(highly_eligible/total)*100:.2f}%)")
    print(f"  • Eligible                : {eligible:>4} ({(eligible/total)*100:.2f}%)")
    print(f"  • Conditionally Eligible  : {conditionally_eligible:>4} ({(conditionally_eligible/total)*100:.2f}%)")
    print(f"Not Eligible Candidates     : {not_eligible:>4} ({(not_eligible/total)*100:.2f}%)")
    print("=" * 65)


if __name__ == "__main__":
    # 1. Run all test cases (Core, Demo Fields, and Boundary tests)
    run_test_cases()

    # 2. Run full dataset screening summary
    run_dataset_screening_summary()
