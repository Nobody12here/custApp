from openpyxl import load_workbook
from CUSTApp.models import Users, Convocation
from typing import Tuple


def load_convocation_data(file_path: str, convocation: Convocation) -> Tuple:

    total_rows = 0
    users_modified = 0
    wb = load_workbook(filename=file_path, read_only=True)
    active = wb.active
    header = next(active.iter_rows(min_row=1, max_row=1, values_only=True))

    reg_idx = header.index("Registration No.")
    whatsapp_idx = header.index("Whatsapp Number")
    email_idx = header.index("Email Address")
    is_eligible_idx = header.index("Will you attend the Convocation?")
    for rows in active.iter_rows(min_row=2, values_only=True):  # Skip the header row
        reg_no = rows[reg_idx]

        try:
            user = Users.objects.get(uu_id=reg_no)
            # Update stuff
            if rows[is_eligible_idx].lower() == "yes":
                user.convocation = convocation
            user.secondary_email = rows[email_idx]
            user.phone_number = rows[whatsapp_idx]
            user.save()
            users_modified += 1
            print(f"{user.name} -- {user.phone_number}")
        except Users.DoesNotExist:
            print(f"The user with this {reg_no} does not exists")
            continue
        total_rows += 1
    return (total_rows, users_modified)


convocation = Convocation.objects.first()
load_convocation_data("convocation.xlsx", convocation)
