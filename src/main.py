"""
Scholarship Eligibility Screening System
Module: main.py
Phase: 8 - Main Application and Menu-Driven Interface

Description:
    This is the master entry point for the BCA college Python project:
    "Scholarship Eligibility Screening System Using Rule-Based Conditions".
    
    It integrates all completed project modules (Phases 1 through 7) into a
    robust, interactive, menu-driven console application tailored for practical
    examinations and viva voce demonstrations.
    
Key Architecture:
    - LOADS ONCE AT STARTUP: Evaluates all 6,607 student records once upon launch
      and maintains the evaluated profiles in memory for instant menu operations.
    - REUSES EXISTING MODULES: Delegates directly to Phase 1 (inspect_dataset),
      Phase 2 (data_loader, validation), Phases 3-5 (eligibility),
      Phase 6 (ranking), and Phase 7 (report).
    - DEFENSIVE INPUT HANDLING: Catches non-numeric menu choices, empty inputs,
      invalid student IDs, and out-of-range pagination requests safely.
    - ZERO EXTERNAL DEPENDENCIES: Pure Python standard library (os, sys, datetime).
    - IMMUTABILITY: Never alters the original Kaggle CSV dataset.

Author: BCA Student Developer
Advisor: Senior Python Developer & Mentor
"""

import os
import sys
from datetime import datetime

# Path resolution to ensure local 'src' modules import cleanly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import required functions from previous completed phases
from data_loader import load_students
from eligibility import (
    calculate_eligibility,
    evaluate_all_students,
    display_single_result
)
from ranking import (
    rank_by_category,
    create_overall_merit_list,
    get_cgpa,
    get_attendance,
    get_income,
    get_student_id,
    get_student_name,
    get_classification,
    get_eligibility_score
)
from report import (
    generate_summary,
    generate_all_reports,
    check_csv_integrity
)


# =============================================================================
# HELPER & INPUT VALIDATION UTILITIES
# =============================================================================

def normalize_student_id(raw_input):
    """
    Normalizes a user-entered Student ID string.
    Handles lowercase, whitespace, and bare numbers.
    
    Examples:
        'stu0001' -> 'STU0001'
        '1'       -> 'STU0001'
        'STU1'    -> 'STU0001'
        'STU0001' -> 'STU0001'
        
    Parameters:
        raw_input (str): User input string.
        
    Returns:
        str: Normalized student ID.
    """
    cleaned = raw_input.strip().upper()
    if not cleaned:
        return ""
    if cleaned.isdigit():
        return f"STU{int(cleaned):04d}"
    if cleaned.startswith("STU") and cleaned[3:].isdigit():
        return f"STU{int(cleaned[3:]):04d}"
    return cleaned


def get_user_limit(prompt, default=10, max_val=None):
    """
    Prompts the user for a display limit, safely handling non-numeric or out-of-range input.
    
    Parameters:
        prompt (str): Text prompt to display.
        default (int): Default count if user presses Enter.
        max_val (int, optional): Upper bound for records.
        
    Returns:
        int: Validated integer limit.
    """
    user_input = input(prompt).strip()
    if not user_input:
        return default
    if user_input.lower() in ("all", "a"):
        return max_val if max_val else default

    try:
        val = int(user_input)
        if val <= 0:
            print(f"  [!] Non-positive number entered. Using default of {default}.")
            return default
        if max_val and val > max_val:
            print(f"  [i] Requested {val:,} exceeds available {max_val:,}. Showing all {max_val:,}.")
            return max_val
        return val
    except ValueError:
        print(f"  [!] Invalid number '{user_input}'. Using default of {default}.")
        return default


def pause_prompt():
    """Prompts the user to press Enter before returning to the main menu."""
    input("\nPress [Enter] to return to the Main Menu...")


# =============================================================================
# MENU DISPLAY
# =============================================================================

def display_main_menu():
    """
    Displays the standard system menu required by the project specifications.
    """
    print("\n========================================")
    print(" SCHOLARSHIP ELIGIBILITY SCREENING SYSTEM")
    print("========================================")
    print()
    print("1. Display All Applications")
    print("2. Screen Individual Student")
    print("3. Screen All Students")
    print("4. Search Student")
    print("5. Display Eligible Students")
    print("6. Display Highly Eligible Students")
    print("7. Rank Eligible Students")
    print("8. Display Scholarship Summary")
    print("9. Display Screening Date and Time")
    print("10. Exit")
    print()
    print("========================================")


# =============================================================================
# OPTION 1: DISPLAY ALL APPLICATIONS (WITH CONTROLLED PAGINATION)
# =============================================================================

def handle_display_all_applications(raw_students):
    """
    Menu Option 1: Displays loaded student applications.
    Implements controlled pagination to prevent uncontrolled terminal dumping.
    
    Parameters:
        raw_students (list): List of prepared raw student records.
    """
    total = len(raw_students)
    print("\n" + "=" * 95)
    print(f" DISPLAY ALL APPLICATIONS (Total Records: {total:,})".center(95))
    print("=" * 95)

    limit = get_user_limit(
        f"Enter number of records to view per page (1-{total}, default 10): ",
        default=10,
        max_val=total
    )

    current_idx = 0
    while current_idx < total:
        end_idx = min(current_idx + limit, total)
        print(f"\nDisplaying records {current_idx + 1:,} to {end_idx:,} of {total:,}:")
        print("-" * 95)
        print(
            f"{'No.':<6} | {'Student ID':<10} | {'Student Name':<16} | "
            f"{'CGPA (Demo)':<11} | {'Attendance':<10} | {'Family Income':<14} | {'Status':<8}"
        )
        print("-" * 95)

        for i in range(current_idx, end_idx):
            s = raw_students[i]
            cgpa_str = f"{s.get('Demo_CGPA', 0.0):.2f}" if s.get('Demo_CGPA') is not None else "N/A"
            att_str = f"{s.get('Attendance', 0.0):.1f}%" if s.get('Attendance') is not None else "N/A"
            inc_val = s.get('Demo_Family_Income')
            inc_str = f"Rs. {inc_val:,}" if inc_val is not None else "N/A"
            stat_str = str(s.get('Demo_Enrollment_Status', 'N/A'))

            print(
                f"{i + 1:<6} | {s.get('Student_ID', 'N/A'):<10} | {s.get('Student_Name', 'N/A'):<16} | "
                f"{cgpa_str:<11} | {att_str:<10} | {inc_str:<14} | {stat_str:<8}"
            )

        print("-" * 95)
        current_idx = end_idx

        if current_idx < total:
            choice = input(f"Press [Enter] for next {limit} records, or enter 'm' to stop: ").strip().lower()
            if choice == 'm' or choice == 'q':
                break
        else:
            print("  All requested records have been displayed.")


# =============================================================================
# OPTION 2: SCREEN INDIVIDUAL STUDENT
# =============================================================================

def handle_screen_individual_student(evaluations_by_id):
    """
    Menu Option 2: Screens an individual student by ID and displays
    their validation status, eligibility category, mandatory checks, and explanation.
    
    Parameters:
        evaluations_by_id (dict): Mapping from Student ID string to evaluation record.
    """
    print("\n" + "=" * 70)
    print(" SCREEN INDIVIDUAL STUDENT".center(70))
    print("=" * 70)

    user_input = input("Enter Student ID to evaluate (e.g., STU0001, STU1526): ").strip()
    if not user_input:
        print("  [!] Error: Student ID cannot be empty.")
        return

    sid_norm = normalize_student_id(user_input)
    evaluation = evaluations_by_id.get(sid_norm)

    if evaluation is None:
        print(f"  [!] Student ID '{user_input}' was not found in the dataset.")
        print("      Valid student IDs range from STU0001 to STU6607.")
        return

    # Reuse formatted single result display function from eligibility.py
    display_single_result(evaluation)


# =============================================================================
# OPTION 3: SCREEN ALL STUDENTS (SUMMARY DISPLAY)
# =============================================================================

def handle_screen_all_students(evaluated_students):
    """
    Menu Option 3: Displays summary metrics across all 6,607 records without
    unnecessary terminal flooding.
    
    Parameters:
        evaluated_students (list): List of evaluated student records.
    """
    summary = generate_summary(evaluated_students)
    total = summary["total_applications"]

    print("\n" + "=" * 70)
    print(" SCREEN ALL STUDENTS: COMPREHENSIVE INSTITUTIONAL RESULTS".center(70))
    print("=" * 70)
    print(f"Total Student Profiles Evaluated  : {total:,}")
    print(f"Data Validation Passed (Valid)    : {summary['valid_records']:,} ({(summary['valid_records']/total)*100:.2f}%)")
    print(f"Data Validation Failed (Invalid)  : {summary['invalid_records']:,} ({(summary['invalid_records']/total)*100:.2f}%)")
    print("-" * 70)
    print("Eligibility Classification Distribution:")
    print(f"  • Category 1: Highly Eligible        : {summary['highly_eligible']:>5,} candidates ({(summary['highly_eligible']/total)*100:.2f}%)")
    print(f"  • Category 2: Eligible               : {summary['eligible']:>5,} candidates ({(summary['eligible']/total)*100:.2f}%)")
    print(f"  • Category 3: Conditionally Eligible : {summary['conditionally_eligible']:>5,} candidates ({(summary['conditionally_eligible']/total)*100:.2f}%)")
    print(f"  • Category 4: Not Eligible           : {summary['not_eligible']:>5,} candidates ({(summary['not_eligible']/total)*100:.2f}%)")
    print(f"  • Disqualified (Invalid Record)      : {summary['invalid_records']:>5,} candidates ({(summary['invalid_records']/total)*100:.2f}%)")
    print("-" * 70)
    print(f"TOTAL QUALIFIED CANDIDATES        : {summary['total_eligible']:,} ({(summary['total_eligible']/total)*100:.2f}%)")
    print("=" * 70)


# =============================================================================
# OPTION 4: SEARCH STUDENT (ATTRIBUTES + SCREENING RESULT)
# =============================================================================

def handle_search_student(raw_students_by_id, evaluations_by_id):
    """
    Menu Option 4: Searches student records and presents raw dataset attributes
    alongside the final screening decision.
    
    Parameters:
        raw_students_by_id (dict): Mapping from Student ID to raw prepared record.
        evaluations_by_id (dict): Mapping from Student ID to evaluated record.
    """
    print("\n" + "=" * 75)
    print(" SEARCH STUDENT RECORD".center(75))
    print("=" * 75)

    user_input = input("Enter Student ID to search (e.g., STU0001, STU1526): ").strip()
    if not user_input:
        print("  [!] Error: Student ID cannot be empty.")
        return

    sid_norm = normalize_student_id(user_input)
    raw = raw_students_by_id.get(sid_norm)
    evaluation = evaluations_by_id.get(sid_norm)

    if raw is None or evaluation is None:
        print(f"  [!] No student record found for ID '{user_input}'.")
        print("      Please ensure the ID is between STU0001 and STU6607.")
        return

    is_valid = evaluation.get("is_valid_data", True)
    classification = evaluation.get("classification", "Unknown")

    print(f"\nStudent Search Result for: {sid_norm}")
    print("-" * 75)
    print(f"Student Name            : {raw.get('Student_Name', 'Unknown')}")
    print(f"Hours Studied / Week    : {raw.get('Hours_Studied', 'N/A')}")
    print(f"Attendance Rate         : {raw.get('Attendance', 'N/A')}%")
    print(f"Sleep Hours / Day       : {raw.get('Sleep_Hours', 'N/A')}")
    print(f"Previous Exam Scores    : {raw.get('Previous_Scores', 'N/A')}")
    print(f"Tutoring Sessions       : {raw.get('Tutoring_Sessions', 'N/A')}")
    print(f"Extracurricular Activity: {raw.get('Extracurricular_Activities', 'N/A')}")
    print(f"Original Income Bracket : {raw.get('Family_Income', 'N/A')}")
    print(f"Exam Score (Kaggle)     : {raw.get('Exam_Score', 'N/A')}")
    print("-" * 75)
    print("Synthetic Demonstration Proxies (For College Rule-Based Demo):")
    print(f"  • Demo_CGPA           : {raw.get('Demo_CGPA', 'N/A')}")
    print(f"  • Demo_Family_Income  : Rs. {raw.get('Demo_Family_Income', 0):,}")
    print(f"  • Demo_Backlogs       : {raw.get('Demo_Backlogs', 'N/A')}")
    print(f"  • Demo_Enrollment     : {raw.get('Demo_Enrollment_Status', 'N/A')}")
    print("-" * 75)
    print(f"Validation Status       : {'VALID RECORD' if is_valid else 'INVALID RECORD'}")
    print(f"Screening Decision      : {classification.upper()}")
    score_info = evaluation.get("eligibility_score", {})
    score_val = score_info.get("total_score", 0.0) if isinstance(score_info, dict) else float(score_info or 0.0)
    print(f"Eligibility Score       : {score_val:.2f} / 100.00 (Phase 5 Scoring Engine)")
    print(f"Decision Justification  : {evaluation.get('explanation', '')}")
    print("=" * 75)


# =============================================================================
# OPTION 5: DISPLAY ELIGIBLE STUDENTS (ELIGIBLE & CONDITIONALLY ELIGIBLE)
# =============================================================================

def handle_display_eligible_students(ranked_categories, overall_ranks_by_id):
    """
    Menu Option 5: Displays students classified as Eligible and Conditionally Eligible.
    Explicitly excludes Highly Eligible students (who have their own option).
    Displays the OVERALL merit rank for each candidate.
    
    Parameters:
        ranked_categories (dict): Ranked candidates grouped by category.
        overall_ranks_by_id (dict): Mapping of student_id to institutional overall rank.
    """
    eligible_list = ranked_categories.get("Eligible", [])
    cond_list = ranked_categories.get("Conditionally Eligible", [])

    total_eligible = len(eligible_list)
    total_cond = len(cond_list)
    total_combined = total_eligible + total_cond

    print("\n" + "=" * 95)
    print(f" DISPLAY ELIGIBLE STUDENTS (Eligible: {total_eligible:,} | Conditionally Eligible: {total_cond:,})".center(95))
    print("=" * 95)
    print("Rank is by category and tie-breakers; Score is informational.")
    print("Note: Highly Eligible students are shown separately in Menu Option 6.")

    limit = get_user_limit(
        f"\nEnter number of records to display (default 10, total {total_combined:,}): ",
        default=10,
        max_val=total_combined
    )

    # Combine both tiers for display
    combined = eligible_list + cond_list
    display_records = combined[:limit]

    print("\n" + "-" * 95)
    print(
        f"{'No.':<4} | {'Rank':<6} | {'Student ID':<10} | {'Student Name':<15} | "
        f"{'Score':<6} | {'CGPA':<5} | {'Attnd':<6} | {'Eligibility Category':<22}"
    )
    print("-" * 95)

    for idx, s in enumerate(display_records, start=1):
        sid = get_student_id(s)
        rank_val = overall_ranks_by_id.get(sid, s.get("rank", "-"))
        sname = get_student_name(s)[:14]
        score_str = f"{get_eligibility_score(s):.1f}"
        cgpa_val = f"{get_cgpa(s):.2f}"
        att_val = f"{get_attendance(s):.1f}%"
        cat_val = get_classification(s)

        print(
            f"{idx:<4} | #{rank_val:<5} | {sid:<10} | {sname:<15} | "
            f"{score_str:<6} | {cgpa_val:<5} | {att_val:<6} | {cat_val:<22}"
        )

    print("-" * 95)
    print(f"Displayed {len(display_records):,} of {total_combined:,} eligible candidates.")


# =============================================================================
# OPTION 6: DISPLAY HIGHLY ELIGIBLE STUDENTS
# =============================================================================

def handle_display_highly_eligible_students(ranked_categories, overall_ranks_by_id):
    """
    Menu Option 6: Displays only students classified as Highly Eligible.
    Displays the OVERALL merit rank for each candidate.
    
    Parameters:
        ranked_categories (dict): Ranked candidates grouped by category.
        overall_ranks_by_id (dict): Mapping of student_id to institutional overall rank.
    """
    highly_eligible = ranked_categories.get("Highly Eligible", [])
    total = len(highly_eligible)

    print("\n" + "=" * 85)
    print(f" HIGHLY ELIGIBLE SCHOLARS (Total: {total})".center(85))
    print("=" * 85)
    print("Rank is by category and tie-breakers; Score is informational.")
    print("Criteria: CGPA >= 8.50, Attendance >= 85%, All Mandatory Conditions Satisfied")
    print("-" * 85)
    print(
        f"{'Rank':<6} | {'Student ID':<10} | {'Student Name':<16} | "
        f"{'Score':<7} | {'CGPA':<6} | {'Attendance':<10} | {'Family Income':<14}"
    )
    print("-" * 85)

    if not highly_eligible:
        print("  (No Highly Eligible candidates found)")
    else:
        for s in highly_eligible:
            sid = get_student_id(s)
            rank_val = f"#{overall_ranks_by_id.get(sid, s.get('rank', '-'))}"
            sname = get_student_name(s)[:15]
            score_str = f"{get_eligibility_score(s):.1f}"
            cgpa_val = f"{get_cgpa(s):.2f}"
            att_val = f"{get_attendance(s):.1f}%"
            inc_val = f"Rs. {get_income(s):,}"

            print(
                f"{rank_val:<6} | {sid:<10} | {sname:<16} | "
                f"{score_str:<7} | {cgpa_val:<6} | {att_val:<10} | {inc_val:<14}"
            )

    print("=" * 85)


# =============================================================================
# OPTION 7: RANK ELIGIBLE STUDENTS (CONSOLIDATED MERIT LIST)
# =============================================================================

def handle_rank_eligible_students(overall_merit_list, overall_ranks_by_id=None):
    """
    Menu Option 7: Displays the institutional consolidated merit list
    preserving category tiers and tie-breaking hierarchy.
    
    Parameters:
        overall_merit_list (list): Consolidated merit list from Phase 6.
        overall_ranks_by_id (dict, optional): Mapping of student_id to institutional overall rank.
    """
    total = len(overall_merit_list)
    print("\n" + "=" * 100)
    print(f" CONSOLIDATED SCHOLARSHIP MERIT LIST (Total Ranked: {total:,})".center(100))
    print("=" * 100)
    print("Rank is by category and tie-breakers; Score is informational.")
    print("Institutional Merit Policy:")
    print("  Tier 1: Highly Eligible  ->  Tier 2: Eligible  ->  Tier 3: Conditionally Eligible")
    print("  Tie-Breakers: 1. Higher CGPA | 2. Higher Attendance | 3. Lower Income | 4. Student ID")

    limit = get_user_limit(
        f"\nEnter number of ranked scholars to view (default 15, max {total:,}): ",
        default=15,
        max_val=total
    )

    display_list = overall_merit_list[:limit]

    print("\n" + "-" * 100)
    print(
        f"{'Rank':<6} | {'Student ID':<10} | {'Student Name':<15} | "
        f"{'Score':<6} | {'Classification':<22} | {'CGPA':<5} | {'Attnd':<6} | {'Income (INR)':<12}"
    )
    print("-" * 100)

    for s in display_list:
        sid = get_student_id(s)
        if overall_ranks_by_id and sid in overall_ranks_by_id:
            rank_num = overall_ranks_by_id[sid]
        else:
            rank_num = s.get("rank", "-")
        rank_val = f"#{rank_num}"
        sname = get_student_name(s)[:14]
        score_str = f"{get_eligibility_score(s):.1f}"
        cls_val = get_classification(s)[:21]
        cgpa_val = f"{get_cgpa(s):.2f}"
        att_val = f"{get_attendance(s):.1f}%"
        inc_val = f"Rs. {get_income(s):,}"

        print(
            f"{rank_val:<6} | {sid:<10} | {sname:<15} | "
            f"{score_str:<6} | {cls_val:<22} | {cgpa_val:<5} | {att_val:<6} | {inc_val:<12}"
        )

    print("-" * 100)
    print(f"Displayed Top {len(display_list):,} of {total:,} ranked scholars.")


# =============================================================================
# OPTION 8: DISPLAY SCHOLARSHIP SUMMARY & OPTIONAL REPORT GENERATION
# =============================================================================

def handle_display_scholarship_summary(evaluated_students):
    """
    Menu Option 8: Displays scholarship screening summary metrics,
    and asks the user whether they want to generate permanent official reports.
    
    Parameters:
        evaluated_students (list): List of evaluated student records.
    """
    summary = generate_summary(evaluated_students)
    total = summary["total_applications"]
    valid = summary["valid_records"]
    invalid = summary["invalid_records"]
    tot_eligible = summary["total_eligible"]
    ineligible = summary["not_eligible"]

    print("\n" + "=" * 70)
    print(" SCHOLARSHIP SCREENING SUMMARY METRICS".center(70))
    print("=" * 70)
    print(f"Total Student Applications Processed : {total:,}")
    print(f"Valid Records                        : {valid:,} ({(valid/total)*100:.2f}%)")
    print(f"Invalid Records (Disqualified)       : {invalid:,} ({(invalid/total)*100:.2f}%)")
    print(f"Total Eligible Candidates            : {tot_eligible:,} ({(tot_eligible/total)*100:.2f}%)")
    print(f"Total Ineligible Candidates          : {ineligible:,} ({(ineligible/total)*100:.2f}%)")
    print("-" * 70)
    print("Category Breakdown:")
    print(f"  • Highly Eligible                  : {summary['highly_eligible']:>5,}")
    print(f"  • Eligible                         : {summary['eligible']:>5,}")
    print(f"  • Conditionally Eligible           : {summary['conditionally_eligible']:>5,}")
    print(f"  • Not Eligible                     : {summary['not_eligible']:>5,}")
    print(f"  • Disqualified (Invalid Record)    : {summary['invalid_records']:>5,}")
    print("=" * 70)

    # Prompt user for report file generation
    gen_choice = input("\nDo you also want to generate the three official report files in 'reports/'? (y/n): ").strip().lower()
    if gen_choice in ("y", "yes"):
        print("\n[System] Generating official timestamped institutional reports...")
        report_results = generate_all_reports(evaluated_students)
        print("\nGenerated File Artifacts:")
        for label, path in report_results.get("generated_files", {}).items():
            print(f"  [+] {label:<22} : {path}")
    else:
        print("  Skipped report file generation. Returning to menu.")


# =============================================================================
# OPTION 9: DISPLAY SCREENING DATE AND TIME
# =============================================================================

def handle_display_datetime():
    """
    Menu Option 9: Displays the current system date and time in DD-MM-YYYY HH:MM:SS format.
    """
    now = datetime.now()
    formatted_dt = now.strftime("%d-%m-%Y %H:%M:%S")

    print("\n" + "=" * 60)
    print(" SYSTEM SCREENING DATE & TIME".center(60))
    print("=" * 60)
    print(f"Current Date and Time : {formatted_dt}")
    print(f"Calendar Day          : {now.strftime('%A')}")
    print("Standard Timezone     : Local System Time")
    print("=" * 60)


# =============================================================================
# MAIN APPLICATION CONTROLLER
# =============================================================================

def main():
    """
    Main application loop.
    Loads and evaluates the student dataset once at launch, then runs the CLI menu loop.
    """
    print("\n" + "=" * 80)
    print(" INITIALIZING SCHOLARSHIP ELIGIBILITY SCREENING SYSTEM ")
    print("=" * 80)

    # Verify baseline CSV integrity before startup
    csv_file = "dataset/original_dataset.csv"
    is_intact, current_hash = check_csv_integrity(csv_file)
    if is_intact:
        print("[System] Kaggle CSV dataset verified intact (SHA-256 matches baseline).")
    else:
        print(f"[Warning] Dataset integrity check returned: {current_hash}")

    # Load dataset ONCE
    print("[System] Loading student records from 'dataset/original_dataset.csv'...")
    raw_students = load_students()
    total_raw = len(raw_students)
    print(f"[System] Successfully loaded {total_raw:,} student records.")

    # Evaluate all records ONCE
    print("[System] Evaluating eligibility using Phases 3-5 deterministic rules engine...")
    evaluated_students = evaluate_all_students(raw_students)
    print(f"[System] Evaluated {len(evaluated_students):,} student profiles into memory.")

    # Generate ranking data ONCE
    print("[System] Precomputing Phase 6 merit ranking and category tiers...")
    ranked_categories = rank_by_category(evaluated_students)
    overall_merit_list = create_overall_merit_list(evaluated_students)
    overall_ranks_by_id = {get_student_id(s): s.get("rank") for s in overall_merit_list}
    print(f"[System] Precomputed {len(overall_merit_list):,} ranked eligible scholars.")

    # Fast ID lookup maps
    raw_students_by_id = {get_student_id(s).upper(): s for s in raw_students}
    evaluations_by_id = {get_student_id(e).upper(): e for e in evaluated_students}

    print("\n[System] All data structures loaded and cached successfully. Starting interface...")

    # Main Interactive Menu Loop with clean exit on interrupt/EOF
    try:
        while True:
            display_main_menu()
            choice = input("Enter your choice (1-10): ").strip()

            if choice == "1":
                handle_display_all_applications(raw_students)
                pause_prompt()

            elif choice == "2":
                handle_screen_individual_student(evaluations_by_id)
                pause_prompt()

            elif choice == "3":
                handle_screen_all_students(evaluated_students)
                pause_prompt()

            elif choice == "4":
                handle_search_student(raw_students_by_id, evaluations_by_id)
                pause_prompt()

            elif choice == "5":
                handle_display_eligible_students(ranked_categories, overall_ranks_by_id)
                pause_prompt()

            elif choice == "6":
                handle_display_highly_eligible_students(ranked_categories, overall_ranks_by_id)
                pause_prompt()

            elif choice == "7":
                handle_rank_eligible_students(overall_merit_list, overall_ranks_by_id)
                pause_prompt()

            elif choice == "8":
                handle_display_scholarship_summary(evaluated_students)
                pause_prompt()

            elif choice == "9":
                handle_display_datetime()
                pause_prompt()

            elif choice == "10":
                print("\n" + "=" * 70)
                print(" Thank you for using the Scholarship Eligibility Screening System.")
                print(" Application session terminated safely. Goodbye!")
                print("=" * 70)
                sys.exit(0)

            elif not choice:
                print("\n  [!] Error: Input cannot be empty. Please enter a choice between 1 and 10.")
                pause_prompt()

            else:
                print(f"\n  [!] Invalid choice '{choice}'. Please select a valid number from 1 to 10.")
                pause_prompt()
    except (KeyboardInterrupt, EOFError):
        print("\n\n" + "=" * 70)
        print(" Thank you for using the Scholarship Eligibility Screening System.")
        print(" Application session terminated safely. Goodbye!")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
