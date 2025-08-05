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
    reg_idx = header.index("uu_id")
    name_idx = header.index("Name")
    gender_idx = header.index("Gender")
    father_name_idx = header.index("Father Name")
    email_idx = header.index("Email personal")
    designation_idx = header.index("designation")

    for rows in active.iter_rows(min_row=2, values_only=True):  # Skip the header row
        reg_no = rows[reg_idx]
        name = rows[name_idx]
        father_name = rows[father_name_idx]
        email = rows[email_idx]
        gender = rows[gender_idx]
        designation = rows[designation_idx]
        user_type = "Staff"
        try:
            Users.objects.update_or_create(
            email=email,
            defaults={
                "uu_id": reg_no,
                "name": name,
                "father_name": father_name,
                "email": email,
                "user_type": user_type,
                "gender":gender,
                "designation":designation
            },
        )
            print("Updated or created sucessfully! for email = ",email)
        except Users.MultipleObjectsReturned:
            print("Multiple objects returned for this email ",email)
            continue
    print("-" * 10)
    print(f"Total rows  = {total_rows}")
    print(f"Total Users updated present in the DB {total_updated}")
    print(f"Total users to add = {not_exists}")


upload_student_data('../../Faculty.xlsx')
