import sys
import os
import pandas as pd
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.main import app, db
from src.models.student import Student

EXCEL_FILE_PATH = "/home/ubuntu/upload/Sidanira_LegerSemester_1_3269.xlsx"
SHEET_NAME = "Table 1"
HEADER_ROW = 2 # 0-based index, so row 3 is index 2

# Define the new fields requested by the user
NEW_FIELDS = [
    "Prestasi Akademik", "Prestasi Non-Akademik", "Persentil Non Akademik",
    "OSIS dan MPK", "Ekskul", "Kejuaraan", "Seleksi Ketat Non Kejuaraan"
]

def load_student_data():
    try:
        df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=SHEET_NAME, header=HEADER_ROW)

        # Rename columns for clarity based on analysis
        df.rename(columns={"Unnamed: 1": "student_id", "Unnamed: 2": "name"}, inplace=True)

        # Drop rows where student_id or name might be missing
        df.dropna(subset=["student_id", "name"], inplace=True)

        # Ensure student_id is treated as string and clean it
        df["student_id"] = df["student_id"].apply(lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (float, int)) else str(x))

        updated_count = 0
        added_count = 0

        with app.app_context():
            for index, row in df.iterrows():
                student_id_val = row["student_id"]
                name_val = row["name"]

                # Prepare the JSON data for the rest of the columns
                scores_dict = row.drop(["student_id", "name"]).to_dict()
                scores_json_serializable = {}
                for k, v in scores_dict.items():
                    # Clean column names (remove potential leading/trailing spaces)
                    clean_k = str(k).strip() if k else k
                    if pd.isna(v):
                        scores_json_serializable[clean_k] = None
                    elif isinstance(v, (int, float, complex)):
                        # Check for numpy types specifically if needed
                        if hasattr(v, "item"): # Check if it is a numpy type
                            scores_json_serializable[clean_k] = v.item() # Convert numpy type to Python native type
                        else:
                            scores_json_serializable[clean_k] = v # Keep standard Python numbers
                    else:
                        scores_json_serializable[clean_k] = str(v)

                # Add new fields with default empty string if they don"t exist
                for field in NEW_FIELDS:
                    if field not in scores_json_serializable:
                        scores_json_serializable[field] = "" # Default empty value

                # Check if student already exists
                existing_student = Student.query.filter_by(student_id=student_id_val).first()
                if existing_student:
                    # Update existing student"s scores_data
                    needs_update = False
                    current_data = existing_student.scores_data if isinstance(existing_student.scores_data, dict) else {}

                    # Check if any new field is missing or if data needs merging/overwriting
                    for field in NEW_FIELDS:
                        # Add if missing or if existing value is None/empty string
                        if field not in current_data or current_data[field] is None or current_data[field] == "":
                            # Use value from Excel if available and not None/NaN, otherwise use default empty string
                            excel_value = scores_json_serializable.get(field)
                            current_data[field] = excel_value if excel_value is not None else ""
                            needs_update = True

                    # Optionally, update all fields from Excel (overwrite strategy)
                    # current_data.update(scores_json_serializable)
                    # needs_update = True # Assume update is always needed if overwriting

                    if needs_update:
                        print(f"Updating existing student: {student_id_val} - {name_val}")
                        existing_student.scores_data = current_data # Assign the updated dictionary
                        db.session.add(existing_student) # Ensure the session tracks the change
                        updated_count += 1
                    # else:
                        # print(f"Skipping already up-to-date student: {student_id_val} - {name_val}")
                else:
                    # Add new student
                    print(f"Preparing to add new student: {student_id_val} - {name_val}")
                    new_student = Student(
                        student_id=student_id_val,
                        name=name_val,
                        scores_data=scores_json_serializable
                    )
                    db.session.add(new_student)
                    added_count += 1

            # Commit all changes (adds and updates)
            if added_count > 0 or updated_count > 0:
                db.session.commit()
                print(f"Successfully added {added_count} new students.")
                print(f"Successfully updated {updated_count} existing students with new fields.")
            else:
                print("No new students added or existing students updated.")

    except FileNotFoundError:
        print(f"Error: Excel file not found at {EXCEL_FILE_PATH}")
    except Exception as e:
        print(f"An error occurred during data loading: {e}")
        with app.app_context():
            db.session.rollback()

if __name__ == "__main__":
    print("Starting student data loading/updating...")
    load_student_data()
    print("Student data loading/updating finished.")

