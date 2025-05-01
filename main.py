from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_required
from src.models.student import Student
from src.extensions import db
import json
# import pandas as pd # Moved inside download_excel
from io import BytesIO
from weasyprint import HTML, CSS
import os

main_bp = Blueprint("main", __name__)

# --- Existing Routes --- 

@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@main_bp.route("/students")
@login_required
def list_students():
    students = Student.query.all()
    return render_template("students.html", students=students)

@main_bp.route("/add_student", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        student_id = request.form.get("student_id")
        name = request.form.get("name")
        scores_data = {}
        # Add default empty values for new fields
        new_fields = [
            "Prestasi Akademik", "Prestasi Non-Akademik", "Persentil Non Akademik",
            "OSIS dan MPK", "Ekskul", "Kejuaraan", "Seleksi Ketat Non Kejuaraan"
        ]
        for field in new_fields:
            scores_data[field] = ""

        if not student_id or not name:
            flash("Student ID and Name are required.", "danger")
            return render_template("add_student.html")

        existing_student = Student.query.filter_by(student_id=student_id).first()
        if existing_student:
            flash(f"Student with ID {student_id} already exists.", "warning")
            return render_template("add_student.html", student_id=student_id, name=name)

        try:
            new_student = Student(student_id=student_id, name=name, scores_data=scores_data)
            db.session.add(new_student)
            db.session.commit()
            flash(f"Student {name} added successfully.", "success")
            return redirect(url_for("main.list_students"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding student: {e}", "danger")

    return render_template("add_student.html")

@main_bp.route("/edit_student/<int:student_id_db>", methods=["GET", "POST"])
@login_required
def edit_student(student_id_db):
    student = Student.query.get_or_404(student_id_db)

    if request.method == "POST":
        original_student_id = student.student_id
        new_student_id = request.form.get("student_id")
        new_name = request.form.get("name")
        scores_data_str = request.form.get("scores_data", "{}")

        if not new_student_id or not new_name:
            flash("Student ID and Name are required.", "danger")
            return render_template("edit_student.html", student=student, scores_data_str=scores_data_str)

        if new_student_id != original_student_id:
            existing_student = Student.query.filter_by(student_id=new_student_id).first()
            if existing_student:
                flash(f"Another student with ID {new_student_id} already exists.", "warning")
                student.student_id = new_student_id
                student.name = new_name
                return render_template("edit_student.html", student=student, scores_data_str=scores_data_str)

        try:
            try:
                scores_data_json = json.loads(scores_data_str)
                if not isinstance(scores_data_json, dict):
                    raise ValueError("Scores data must be a valid JSON object.")
            except json.JSONDecodeError:
                flash("Invalid JSON format for scores data.", "danger")
                student.student_id = new_student_id
                student.name = new_name
                return render_template("edit_student.html", student=student, scores_data_str=scores_data_str)
            except ValueError as ve:
                flash(str(ve), "danger")
                student.student_id = new_student_id
                student.name = new_name
                return render_template("edit_student.html", student=student, scores_data_str=scores_data_str)

            student.student_id = new_student_id
            student.name = new_name
            student.scores_data = scores_data_json

            db.session.commit()
            flash(f"Student {student.name} updated successfully.", "success")
            return redirect(url_for("main.list_students"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating student: {e}", "danger")
            student.student_id = original_student_id
            return render_template("edit_student.html", student=student, scores_data_str=scores_data_str)

    scores_data_str = json.dumps(student.scores_data, indent=4, ensure_ascii=False) if student.scores_data else "{}"
    return render_template("edit_student.html", student=student, scores_data_str=scores_data_str)

# --- Download Routes --- 

@main_bp.route("/download/excel")
@login_required
def download_excel():
    import pandas as pd # Import pandas here
    students = Student.query.all()
    if not students:
        flash("No student data to export.", "warning")
        return redirect(url_for("main.list_students"))

    # Prepare data for DataFrame
    data_list = []
    # Define the order and names of columns based on Sidanira_25.pdf and requirements
    column_mapping = {
        "student_id": "ID Siswa",
        "name": "Nama Siswa",
        "NILAI": "PAI", 
        "Unnamed: 4": "PKN",
        "Unnamed: 5": "BIN",
        "Unnamed: 6": "MAT",
        "Unnamed: 7": "IPA",
        "Unnamed: 8": "IPS",
        "NILAI.1": "BIG",
        "Unnamed: 10": "SBD",
        "Unnamed: 11": "PJK",
        "Unnamed: 12": "PRK", 
        # Add other relevant score columns from scores_data if needed
        "TOTAL": "Total Nilai",
        "RERATA NILAI RAPORT (30%)": "Rerata Raport",
        "Prestasi Akademik": "Prestasi Akademik",
        "Prestasi Non-Akademik": "Prestasi Non-Akademik",
        "Persentil Non Akademik": "Persentil Non Akademik",
        "OSIS dan MPK": "OSIS/MPK",
        "Ekskul": "Ekskul",
        "Kejuaraan": "Kejuaraan",
        "Seleksi Ketat Non Kejuaraan": "Seleksi Ketat Non Kejuaraan"
    }

    for student in students:
        student_data = {"ID Siswa": student.student_id, "Nama Siswa": student.name}
        scores = student.scores_data if isinstance(student.scores_data, dict) else {}
        for original_key, display_name in column_mapping.items():
            if original_key not in ["student_id", "name"]:
                student_data[display_name] = scores.get(original_key, None)
        data_list.append(student_data)

    df = pd.DataFrame(data_list)
    ordered_columns = [col for col in column_mapping.values() if col in df.columns]
    df = df[ordered_columns]

    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sidanira Data")
        # Optional: Auto-adjust columns width
        # worksheet = writer.sheets["Sidanira Data"]
        # for i, col in enumerate(df.columns):
        #     column_len = max(df[col].astype(str).map(len).max(), len(col))
        #     worksheet.column_dimensions[chr(65 + i)].width = column_len + 2

    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="Sidanira_Data.xlsx"
    )

@main_bp.route("/download/pdf")
@login_required
def download_pdf():
    students = Student.query.all()
    if not students:
        flash("No student data to export.", "warning")
        return redirect(url_for("main.list_students"))

    # Render an HTML template designed for PDF export
    headers = [
        "No", "ID Siswa", "Nama Siswa", "PAI", "PKN", "BIN", "MAT", "IPA", "IPS", "BIG", "SBD", "PJK", "PRK",
        "Total", "Rerata",
        "Prestasi Akademik", "Prestasi Non-Akademik", "Persentil Non Akademik",
        "OSIS/MPK", "Ekskul", "Kejuaraan", "Seleksi Ketat Non Kejuaraan"
    ]
    key_to_header_map = {
        "student_id": "ID Siswa",
        "name": "Nama Siswa",
        "NILAI": "PAI",
        "Unnamed: 4": "PKN",
        "Unnamed: 5": "BIN",
        "Unnamed: 6": "MAT",
        "Unnamed: 7": "IPA",
        "Unnamed: 8": "IPS",
        "NILAI.1": "BIG",
        "Unnamed: 10": "SBD",
        "Unnamed: 11": "PJK",
        "Unnamed: 12": "PRK",
        "TOTAL": "Total",
        "RERATA NILAI RAPORT (30%)": "Rerata",
        "Prestasi Akademik": "Prestasi Akademik",
        "Prestasi Non-Akademik": "Prestasi Non-Akademik",
        "Persentil Non Akademik": "Persentil Non Akademik",
        "OSIS dan MPK": "OSIS/MPK",
        "Ekskul": "Ekskul",
        "Kejuaraan": "Kejuaraan",
        "Seleksi Ketat Non Kejuaraan": "Seleksi Ketat Non Kejuaraan"
    }

    rendered_html = render_template("export_pdf.html", students=students, headers=headers, key_map=key_to_header_map)

    # Define CSS for PDF styling
    css_string = """
        @import url("https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&display=swap");
        @font-face {
            font-family: NotoSansCJK;
            src: url(/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc);
        }
        body { font-family: "Noto Sans", NotoSansCJK, sans-serif; font-size: 9pt; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 1em; }
        th, td { border: 1px solid #ddd; padding: 4px; text-align: left; word-wrap: break-word; }
        th { background-color: #f2f2f2; font-weight: bold; }
        h1 { text-align: center; font-size: 14pt; margin-bottom: 1.5em; }
        .page-break { page-break-before: always; }
    """
    css = CSS(string=css_string)

    # Generate PDF
    pdf_bytes = HTML(string=rendered_html).write_pdf(stylesheets=[css])

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="Sidanira_Data.pdf"
    )

