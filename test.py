from openpyxl import load_workbook
from CUSTApp.models import Users, Convocation
from typing import Tuple


def upload_student_data(
    file_path: str,
) -> None:

    total_updated = 0
    total_rows = 0
    not_exists = 0
    wb = load_workbook(filename=file_path, read_only=True)
    active = wb.active
    header = next(active.iter_rows(min_row=1, max_row=1, values_only=True))
    reg_idx = header.index("Reg #")
    father_name_idx = header.index("Father Name")
    email_idx = header.index("Personal Email")
    official_email = header.index("Official Email")
    cgpa_idx = header.index("CGPA")
    term_idx = header.index("Academic Term")
    is_active_idx = header.index("Academic Program/Active")

    for rows in active.iter_rows(min_row=2, values_only=True):  # Skip the header row
        reg_no = rows[reg_idx]
        is_active = rows[is_active_idx]
        if is_active:
            try:
                user = Users.objects.get(uu_id=reg_no)
                user.cgpa = rows[cgpa_idx]
                user.secondary_email = rows[email_idx]
                user.father_name = rows[father_name_idx]
                user.term = rows[term_idx]
                if not user.email:
                    user.email = rows[official_email]
                user.save()
                total_updated += 1
            except Users.DoesNotExist:
                print(f"The user with this {reg_no} does not exists")
                not_exists += 1
                continue

            total_rows += 1
        else:
            print(f"The user {reg_no} is not active!")

    print("-" * 10)
    print(f"Total rows  = {total_rows}")
    print(f"Total Users updated present in the DB {total_updated}")
    print(f"Total users to add = {not_exists}")


# student = Users.objects.filter(user_type="Student").count()
# print(f"Number of students = {student}")
# load_convocation_data("students_data.xlsx")
