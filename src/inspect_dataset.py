"""
Scholarship Eligibility Screening System
Module: inspect_dataset.py
Phase: 1 - Project Setup and Kaggle Dataset Inspection

Description:
    This script inspects the raw Kaggle dataset ('Student Performance Factors')
    stored at 'dataset/original_dataset.csv' using only Python standard library
    modules (os, csv). It analyzes column structure, missing values, column
    types, and evaluates dataset compatibility against scholarship screening
    business rules.

Author: BCA Student Developer
Advisor: Senior Python Developer & Mentor
"""

import os
import csv


def get_dataset_path(filename="original_dataset.csv"):
    """
    Locates the dataset file safely across different execution directories.
    
    Checks:
    1. Direct relative path: dataset/<filename>
    2. Relative to the script file location: ../dataset/<filename>
    
    Parameters:
        filename (str): Name of the CSV file to locate.
        
    Returns:
        str: Validated absolute or relative path to the dataset file.
    """
    # Option A: Look relative to the current working directory
    path_from_cwd = os.path.join("dataset", filename)
    if os.path.exists(path_from_cwd):
        return path_from_cwd

    # Option B: Look relative to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path_from_script = os.path.join(script_dir, "..", "dataset", filename)
    if os.path.exists(path_from_script):
        return os.path.normpath(path_from_script)

    # If neither is found, return the default path so caller can raise FileNotFoundError
    return path_from_cwd


def count_records(records):
    """
    Counts the total number of student records loaded.
    
    Parameters:
        records (list): List of student dictionary rows.
        
    Returns:
        int: Number of records.
    """
    # Demonstrating simple built-in len() function
    return len(records)


def display_columns(fieldnames):
    """
    Displays all available dataset columns in a numbered, organized format.
    
    Parameters:
        fieldnames (list): List of column names extracted from CSV header.
    """
    print("\n" + "-" * 50)
    print("2. COLUMN INFORMATION")
    print("-" * 50)
    print(f"Total Columns Detected: {len(fieldnames)}\n")

    # Using for loop with enumerate (starts indexing at 1 for user-friendly display)
    for index, column_name in enumerate(fieldnames, start=1):
        print(f"  [{index:02d}] {column_name}")


def display_sample_records(records, num_records=5):
    """
    Displays the first few records to inspect data formats and sample values.
    
    Parameters:
        records (list): List of student records (dictionaries).
        num_records (int): Number of sample records to display (default: 5).
    """
    print("\n" + "-" * 50)
    print(f"3. SAMPLE RECORDS (First {num_records} Rows)")
    print("-" * 50)

    # Slicing the list to get the first num_records
    sample_slice = records[:num_records]

    # While loop demonstration for sequential display
    i = 0
    while i < len(sample_slice):
        student = sample_slice[i]
        print(f"\n--- [Record #{i + 1}] ---")
        for key, value in student.items():
            # Show '(empty)' if the field has no value
            display_value = value if value.strip() != "" else "(empty)"
            print(f"  {key:<27}: {display_value}")
        i += 1


def check_missing_values(records, fieldnames):
    """
    Counts and reports missing or blank values in each column of the dataset.
    
    Parameters:
        records (list): List of student dictionaries.
        fieldnames (list): Column header names.
        
    Returns:
        dict: Dictionary mapping column name to its count of missing values.
    """
    print("\n" + "-" * 50)
    print("4. MISSING VALUE ANALYSIS")
    print("-" * 50)

    # Initialize dictionary comprehension to store missing count per column
    missing_counts = {col: 0 for col in fieldnames}
    total_rows = len(records)

    # Iterate over all rows to check for empty strings or None values
    for row in records:
        for col in fieldnames:
            val = row.get(col)
            if val is None or val.strip() == "":
                missing_counts[col] += 1

    total_missing_cells = sum(missing_counts.values())
    print(f"Total Missing Cells Across Dataset: {total_missing_cells}\n")

    # Display columns with their missing counts and percentages
    columns_with_missing = 0
    for col, count in missing_counts.items():
        percentage = (count / total_rows) * 100 if total_rows > 0 else 0.0
        status = "OK" if count == 0 else f"MISSING {count} ({percentage:.2f}%)"
        print(f"  {col:<27}: {status}")
        if count > 0:
            columns_with_missing += 1

    if columns_with_missing == 0:
        print("\n  >> Excellent: Dataset has complete data across all columns!")
    else:
        print(f"\n  >> Note: {columns_with_missing} column(s) have missing values.")

    return missing_counts


def identify_column_types(records, fieldnames):
    """
    Identifies whether each column is Numerical or Categorical by inspecting
    the non-empty values across the records.
    
    Parameters:
        records (list): List of student dictionaries.
        fieldnames (list): Column header names.
        
    Returns:
        tuple: (list_of_numerical_columns, list_of_categorical_columns)
    """
    print("\n" + "-" * 50)
    print("5. COLUMN CLASSIFICATION")
    print("-" * 50)

    numerical_columns = []
    categorical_columns = []
    categorical_unique_values = {}

    for col in fieldnames:
        # Find non-empty sample values for this column
        is_numeric = True
        sample_values_found = 0

        for row in records:
            val = row.get(col, "").strip()
            if val != "":
                sample_values_found += 1
                try:
                    # Attempt to convert to float to test for numeric data
                    float(val)
                except ValueError:
                    is_numeric = False
                    break

        # If sample values were found and all were convertible to float, it's numerical
        if sample_values_found > 0 and is_numeric:
            numerical_columns.append(col)
        else:
            categorical_columns.append(col)
            # Collect unique values for categorical columns (up to reasonable set)
            unique_set = set()
            for row in records:
                val = row.get(col, "").strip()
                if val:
                    unique_set.add(val)
            categorical_unique_values[col] = sorted(list(unique_set))

    # Display Numerical Columns
    print(f"Numerical Columns ({len(numerical_columns)}):")
    for col in numerical_columns:
        print(f"  • {col}")

    # Display Categorical Columns with their unique discrete classes
    print(f"\nCategorical Columns ({len(categorical_columns)}):")
    for col in categorical_columns:
        unique_vals = categorical_unique_values.get(col, [])
        vals_preview = ", ".join(f"'{v}'" for v in unique_vals)
        print(f"  • {col:<25} -> Values: [{vals_preview}]")

    return numerical_columns, categorical_columns


def identify_scholarship_fields(fieldnames):
    """
    Compares the mandatory and additional scholarship screening criteria
    against the actual columns present in the Kaggle dataset.
    
    Parameters:
        fieldnames (list): Available CSV column headers.
    """
    print("\n" + "-" * 50)
    print("6. SCHOLARSHIP FIELD ANALYSIS")
    print("-" * 50)

    # Define scholarship criteria and their status against Kaggle dataset
    direct_fields = [
        ("Attendance", "Attendance", "Present as 'Attendance' (Values: 60 - 100%) - Directly satisfies rule 'Attendance >= 75%'."),
        ("Extracurricular Achievement", "Extracurricular_Activities", "Present as 'Extracurricular_Activities' (Values: 'Yes'/'No') - Direct binary indicator.")
    ]

    partially_available_fields = [
        ("Academic Merit (CGPA)", "Exam_Score / Previous_Scores", "Dataset has Exam_Score (44-101) & Previous_Scores (40-100) on a 100-point scale, NOT a college CGPA (0.00 - 10.00 scale)."),
        ("Family Income", "Family_Income", "Dataset has categorical bins ('Low', 'Medium', 'High'), NOT numerical annual rupee income (<= ₹5,00,000)."),
        ("Disability Status", "Learning_Disabilities", "Dataset tracks 'Learning_Disabilities' ('Yes'/'No'), but lacks physical/locomotor/visual disability status."),
        ("First-Generation Learner", "Parental_Education_Level", "Dataset has 'Parental_Education_Level' ('High School', 'College', 'Postgraduate'), from which first-gen status can be inferred, but is not explicitly declared.")
    ]

    missing_fields = [
        ("Academic Backlogs", "None", "No backlog / arrear course count present. Rule requires 'Backlogs <= 1'."),
        ("Enrollment Status", "None", "No academic status column. Rule requires 'Status == Active'."),
        ("Student Identifier", "None", "No Student_ID / Roll_Number or Name column exists in the Kaggle dataset."),
        ("Previous Scholarship Status", "None", "No record of prior financial aid or scholarship history.")
    ]

    print("Available Fields (Direct Match):")
    for requirement, column_name, note in direct_fields:
        print(f"  [DIRECT] {requirement:<28} -> Column: '{column_name}'")
        print(f"           Details: {note}")

    print("\nPartially Available Fields (Related but Insufficient / Different Scale):")
    for requirement, column_name, note in partially_available_fields:
        print(f"  [PARTIAL] {requirement:<27} -> Column: '{column_name}'")
        print(f"            Details: {note}")

    print("\nMissing Fields (Unavailable in Kaggle Dataset):")
    for requirement, column_name, note in missing_fields:
        print(f"  [MISSING] {requirement:<27} -> Column: '{column_name}'")
        print(f"            Details: {note}")


def display_dataset_summary(total_records, total_columns, missing_counts):
    """
    Prints a clear, academic conclusion regarding the dataset suitability
    for the proposed scholarship screening project.
    """
    print("\n" + "-" * 50)
    print("7. DATASET SUMMARY")
    print("-" * 50)
    print("Suitability Evaluation:")
    print("  1. Dataset Size & Integrity:")
    print(f"     - Total student records : {total_records}")
    print(f"     - Total feature columns : {total_columns}")
    total_missing = sum(missing_counts.values())
    print(f"     - Total missing entries : {total_missing}")
    print("     - The Kaggle 'Student Performance Factors' dataset provides a rich, realistic")
    print("       foundation of real-world academic and socio-economic distributions.")
    print("\n  2. Project Alignment & Feasibility:")
    print("     - The dataset directly provides Attendance and Extracurricular participation.")
    print("     - However, key scholarship fields required by college screening criteria are missing:")
    print("       * Unique Student ID / Roll Number")
    print("       * College CGPA (0.00 to 10.00 scale)")
    print("       * Exact Annual Family Income in Rupees (INR)")
    print("       * Current Academic Backlogs Count")
    print("       * Enrollment Status (Active / Inactive)")
    print("\n  3. Architectural Recommendation for Phase 2 (Data Loader):")
    print("     - In Phase 2, we will develop a clean 'data_loader.py' pipeline that safely reads")
    print("       'original_dataset.csv' without modifying it, and systematically maps/enriches")
    print("       the raw records with standard college scholarship attributes (e.g., generating")
    print("       Student IDs like 'STU0001', mapping Exam_Score to realistic CGPA, mapping")
    print("       Family_Income categories to representative rupee amounts, and simulating")
    print("       academic backlogs).")
    print("     - This preserves dataset authenticity while fully enabling deterministic rule-based")
    print("       scholarship screening, ranking, and reporting in subsequent phases.")


def inspect_file():
    """
    Main driver function for Phase 1 dataset inspection.
    
    Coordinates:
    - Path resolution
    - Safe file opening with error handling
    - CSV DictReader parsing with UTF-8-SIG encoding
    - Execution of all analysis and reporting modules
    """
    print("=" * 50)
    print(" SCHOLARSHIP ELIGIBILITY SCREENING SYSTEM")
    print("             DATASET INSPECTION")
    print("=" * 50)

    dataset_path = get_dataset_path()

    print("\n1. DATASET INFORMATION")
    print("-" * 50)
    print(f"Dataset Name          : Student Performance Factors (Kaggle)")
    print(f"File Location         : {dataset_path}")

    # Exception handling for robust, professional file handling
    try:
        # Open with utf-8-sig to automatically handle any UTF-8 BOM if present
        with open(dataset_path, mode="r", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            
            # Check if CSV header is valid
            if reader.fieldnames is None or len(reader.fieldnames) == 0:
                print("\n[ERROR] CSV file appears to be empty or does not have a valid header.")
                return

            fieldnames = reader.fieldnames
            
            # Read all rows into a list of dictionaries
            records = list(reader)

    except FileNotFoundError:
        print(f"\n[ERROR] FileNotFoundError: Dataset file could not be found at '{dataset_path}'.")
        print("Please ensure 'dataset/original_dataset.csv' exists in your project directory.")
        return
    except PermissionError:
        print(f"\n[ERROR] PermissionError: Insufficient permission to read '{dataset_path}'.")
        return
    except UnicodeDecodeError as err:
        print(f"\n[ERROR] UnicodeDecodeError while reading file: {err}")
        return
    except csv.Error as err:
        print(f"\n[ERROR] CSV Parsing Error: {err}")
        return
    except Exception as err:
        print(f"\n[ERROR] An unexpected error occurred: {err}")
        return

    # Check for empty file content
    total_records = count_records(records)
    total_columns = len(fieldnames)

    print(f"Total Student Records : {total_records}")
    print(f"Total Columns         : {total_columns}")

    if total_records == 0:
        print("\n[WARNING] Dataset contains headers but zero student records.")
        return

    # 2. Display all column names
    display_columns(fieldnames)

    # 3. Display first 5 sample records
    display_sample_records(records, num_records=5)

    # 4. Check for missing values
    missing_counts = check_missing_values(records, fieldnames)

    # 5. Identify column data types (numerical vs categorical)
    numerical_cols, categorical_cols = identify_column_types(records, fieldnames)

    # 6. Scholarship requirements analysis
    identify_scholarship_fields(fieldnames)

    # 7. Dataset summary and architectural roadmap
    display_dataset_summary(total_records, total_columns, missing_counts)

    print("\n" + "=" * 50)
    print(" PHASE 1 COMPLETED")
    print("=" * 50)


# Entry point of the script when run directly
if __name__ == "__main__":
    inspect_file()

